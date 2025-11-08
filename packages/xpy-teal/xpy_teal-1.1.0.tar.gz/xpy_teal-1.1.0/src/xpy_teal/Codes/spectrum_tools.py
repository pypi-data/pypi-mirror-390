######################################
#
#   xp_spectral_lines/spectrum_tools.py
#
# Tools translated from Michael Weiler's original R code
# For details of the formalism refer to 
#     https://ui.adsabs.harvard.edu/abs/2023A%26A...671A..52W/abstract
# 
# This implementation:
#     Sagar Malhotra under supervision of Michael Weiler and Friedrich Anders (ICCUB, 2024)
#
######################################
import numpy as np
import ast
from scipy.interpolate import CubicSpline
from .config import _CONFIG
from . import math_tools, line_analysis, download_xp_spectra
from scipy.special import factorial

class XPConstants(object):
    """
    Summarises all the relatively constant objects used in the calculations.
    From Hermite transformation matrices to the LSF.

    Usage examples:
    >>> XPConstants = weiler2023_tools.XPConstants()
    >>> XPConstants.TrafoRP
    >>> XPConstants.get_pseudowavelength(770., instrument="rp", shift=0.)
    """
    def __init__(self, dr="dr3", calib="dr3+weiler2023"):
        """
        Reading everything in ./ConfigurationData/
        """

        #############################################
        # Define Path to Configuration Data
        #############################################

        config_path = _CONFIG['CONFIG_DIR']

        ### First the things that do not change:
        
        # Derivative matrices of the Hermite functions
        self.D1     = np.genfromtxt(config_path / 'DerivativeMatrix_D1.csv', delimiter=',')
        self.D2     = np.genfromtxt(config_path / 'DerivativeMatrix_D2.csv', delimiter=',')
        self.D3     = np.genfromtxt(config_path / 'DerivativeMatrix_D3.csv', delimiter=',')
        self.D4     = np.genfromtxt(config_path / 'DerivativeMatrix_D4.csv', delimiter=',')

        # Matrix used to get the roots of Hermite functions
        self.RootsH = np.genfromtxt(config_path / 'RootMatrix_H.csv', delimiter=',')

        # Hermite integrals
        self.IntsH  = np.genfromtxt(config_path / 'HermiteIntegrals.csv', delimiter=',')


        ################################################################
        # Constructing the P matrix (150x150 matrix for the time being) 
        ################################################################

        P_dim = 150
        P = np.zeros((P_dim, P_dim))
        for i in range(P_dim):
            for j in range(P_dim):
                if np.abs(i - j) == 1:
                    P[i, j] = np.sqrt((min(i, j) + 1)/2)  # All bcz of R. We add 1 to the index to match the R indexing
        
        self.P = P
        
        ### Then things that (probably) depend on the Gaia Data Release
        if dr=="dr3":
            # Transformation matrices for BP and RP
            self.TrafoBP = np.genfromtxt(config_path / 'BasisTransformationMatrix_BP.csv', delimiter=',')
            self.TrafoRP = np.genfromtxt(config_path / 'BasisTransformationMatrix_RP.csv', delimiter=',')
            # Conversion to pseudo-wavelengths
            self.aBP = 3.062231
            self.bBP = 30.00986
            self.aRP = 3.020529
            self.bRP = 30.00292
        else:
            raise ValueError("Unknown 'dr' option")

        if calib=="dr3+weiler2023":
            # Dispersion
            self.DispersionBP = np.genfromtxt(config_path / "bpC03_v375wi_dispersion.csv", delimiter=',').T
            self.DispersionRP = np.genfromtxt(config_path / "rpC03_v142r_dispersion.csv", delimiter=',').T
            # Response function
            self.ResponseBP   = np.genfromtxt(config_path / "bpC03_v375wi_response.csv", delimiter=',').T
            self.ResponseRP   = np.genfromtxt(config_path / "rpC03_v142r_response.csv", delimiter=',').T
            # Line-spread functions
            self.LSFBP        = np.genfromtxt(config_path / "LSFModel_BP.csv", delimiter=',')
            self.LSFRP        = np.genfromtxt(config_path / "LSFModel_RP.csv", delimiter=',')
        else:
            raise ValueError("Unknown 'calib' option")
        
    def get_pseudo_wavelength(self, l, instrument="bp", shift=0.):
        """
        Calculate the pseudowavelength for a given wavelength 
        by interpolating the dispersion relation.
        
        # Arguments:
            l  - Wavelength in nm
        """
        if instrument=="bp":
            return np.interp(l, self.DispersionBP[:,0], self.DispersionBP[:,1]) + shift
        elif instrument=="rp":
            return np.interp(l, self.DispersionRP[:,0], self.DispersionRP[:,1]) + shift

class XP_Spectrum(object):
    """
    Gets all information that can be derived from a
    Gaia XP_CONTINUOUS datalink file.
    That is, this class treats the BP/RP spectra.
    
    Usage:
    """
    def __init__(self, t, setup=None, rotate_basis=True, 
                 truncate=False):
        """
        Initialise an XP spectrum.

        # Inputs:
          t     - datalink table row for XP_CONTINUOUS

        # Optional:
          setup - XP constants object or None
        """
        if setup == None:
            self.setup = XPConstants()
        else:
            self.setup = setup
        # Extract the info from the datalink table: coefficients and correlations
        self.alldata = t
        self.source_id = t["source_id"]
        self.BP      = np.array(t["bp_coefficients"])
        self.RP      = np.array(t["rp_coefficients"])
        self.BP_err  = np.array(t["bp_coefficient_errors"])
        self.RP_err  = np.array(t["rp_coefficient_errors"])
        self.BP_corr = math_tools.create_correlation_matrix(np.array(t["bp_coefficient_correlations"]), 
                                                 len(self.BP))
        self.RP_corr = math_tools.create_correlation_matrix(np.array(t["rp_coefficient_correlations"]), 
                                                 len(self.RP))
        self.BP_cov  = math_tools.corr2cov(self.BP_corr, self.BP_err)
        self.RP_cov  = math_tools.corr2cov(self.RP_corr, self.RP_err)
            
        # Rotate the basis by multiplying the coefficients with
        # the transformation matrix:
        if rotate_basis:
            self.BP     = np.dot(self.setup.TrafoBP.T, self.BP)
            self.RP     = np.dot(self.setup.TrafoRP.T, self.RP)
            self.BP_corr= math_tools.rotate_matrix(self.BP_corr, self.setup.TrafoBP.T)
            self.RP_corr= math_tools.rotate_matrix(self.RP_corr, self.setup.TrafoRP.T)
            self.BP_cov = math_tools.rotate_matrix(self.BP_cov, self.setup.TrafoBP.T)
            self.RP_cov = math_tools.rotate_matrix(self.RP_cov, self.setup.TrafoRP.T)
            self.BP_err = np.sqrt( np.diagonal(self.BP_cov) )
            self.RP_err = np.sqrt( np.diagonal(self.RP_cov) )
        
    def get_internal_spec(self, xx, instrument="bp"):
        """
        Turn the XP coefficients into an internally-calibrated 
        XP spectrum.

        # Inputs:
          xx          - array for calculating Hermite polynomials

        # Optional:
          instrument  - "bp" or "rp"

        # Returns:
          l, internal - pseudo-wavelength, flux 
        """
        # Calculate Hermite functions on the given grid xx
        H = math_tools.HermiteFunction(xx, 55)
        # Transform to pseudo-wavelength
        if instrument == "bp":
            a, b     = self.setup.aBP, self.setup.bBP
            internal = np.dot(H, self.BP)
        elif instrument == "rp":
            a, b     = self.setup.aRP, self.setup.bRP
            internal = np.dot(H, self.RP)
        else:
            raise ValueError("Choose either 'bp' or 'rp' as instrument.")
        l = xx * a + b
        return l, internal


def get_LSF_width(u0, setup=None, instrument="bp", 
                  order=0, n=55, nmax=100, D=0.1):
    """
    Get the width of the line spread function
    at one particular pseudo-wavelength.

    This uses the LSF matrix stored in self.LSFBP/self.LSFRP
    (the LSF is a function of u and u' in Weiler+2023 and can be 
    developed in the same basis of Hermite functions).

    # Parameters:
        u0   - pseudowavelength at which the LSF width is to be computed
    # Optional:
        setup      - XPConstants() object
        instrument - "bp" or "rp"
        order      - 0 or 2
        n          - number of relevant coefficients (default: 55)
        nmax       - maximum number of coefficients needed for the 
                     u' dimension of the LSF (default: 100)
        D          - tolerance (default: 0.1)
    # Returns:
        {'p1':p1, 'p2':p2, 'D':D} - Dictionary
    """
    if setup == None:
        setup = XPConstants()
    if instrument == "bp":
        a   = setup.aBP
        b   = setup.bBP
        LSF = setup.LSFBP[:,:nmax].copy()
    elif instrument == "rp":
        a   = setup.aRP
        b   = setup.bRP
        LSF = setup.LSFRP[:,:nmax].copy()
    # Evaluate the Hermite functions at u0
    H   = math_tools.HermiteFunction(np.array([ (u0-b) / a ]), nmax).ravel() #
    # print(H)
    lsf = np.dot(H, LSF.T)
    # print(lsf.shape)
    # Determine the extrema of the LSF at that point
    if order == 0:
        c1 = np.dot(setup.D1[0:(n+1), 0:(n+1)], np.concatenate((lsf, np.zeros(1))))
        l  = line_analysis.getLinesInNDeriv(c1, np.diag(np.ones(len(c1))), 
                              setup=setup, instrument=instrument)
    elif order == 2:
        c3 = np.dot(setup.D3[0:(n+3), 0:(n+3)], np.concatenate((lsf, np.zeros(3))))
        l  = line_analysis.getLinesInNDeriv(c3, np.diag(np.ones(len(c3))), 
                              setup=setup, instrument=instrument)
    # print(l['estimLinePos'])
    idx1 = np.argmin(np.abs(l['estimLinePos']-u0))
    idx2 = np.argmin(np.abs(l['estimLinePos']-u0+D))
    idx3 = np.argmin(np.abs(l['estimLinePos']-u0-D))

    
    idx = np.unique(np.concatenate(([idx1], [idx2], [idx3])))
    
    return {'p1': l['estimLinePos'][idx[0]], 
            'p2': l['estimLinePos'][idx[1]], 
            'D': np.abs(l['estimLinePos'][idx[0]] - l['estimLinePos'][idx[1]])}


def disp_derivative(u0, order = 1, instrument = 'bp', setup=None, disp_inverse = False):
    '''
    # Computes the derivative of the dispersion relation (interpolated using CubicSpline) at u0
    # Inputs:
    # u0 - psuedo-wavelength
    # order - the order of the derivative (default: 1)
    # instrument - the instrument ("BP" or "RP", needed for the Hermite basis configuration only)
    # setup - the configuration of Hermite basis functions
    '''
    
    cs = disp_u_to_lambda(u0, instrument = instrument, setup=setup, disp_inverse = disp_inverse, return_cs = True)

    return cs.derivative(nu=order)(u0)

def disp_u_to_lambda(u, instrument = 'bp', setup=None, disp_inverse = False, return_cs = False):
    '''
    # Converts pseudo-wavelength to wavelength using the dispersion relation
    The first column of the dispersion relation is the wavelength, the second column is the pseudo-wavelength
    # Inputs:
    # u - psuedo-wavelength or wavelength (if disp_inverse is True)
    # instrument - the instrument ("BP" or "RP", needed for the Hermite basis configuration only)
    # setup - the configuration of Hermite basis functions
    # disp_inverse - if True, converts wavelength to pseudo-wavelength
    # return_cs - if True, returns the CubicSpline object
    '''
    if setup == None:
        setup = XPConstants()
    if instrument == "bp":
        disp = setup.DispersionBP
    elif instrument == "rp":
        disp = setup.DispersionRP

    if not disp_inverse:
        x, y = disp[:,1], disp[:,0]    # pseudo-wavelength, wavelength
    else:
        x, y = disp[:,0], disp[:,1]    # wavelength, pseudo-wavelength
    x_sorted, y_sorted = zip(*sorted(zip(x, y)))
    cs = CubicSpline(x_sorted, y_sorted)

    if return_cs:
        return cs
    else:
        return cs(u)



def get_LKL_elements(u0, k, l, setup = None, instrument = "bp", n = 55, nmax = 100, scale_lsf = False):
    '''
    # Computes the integrals over ∫ L^(k)(u-u0)^l du
    # These are the elements of the matrix 𝔏 Up to a factorial)
    # Inputs:
    # k - the derivative (k=0,1,2,3 is currently implemented)
    # l - the power of (u-u0) (l=0,1,2,3 is currently implemented)
    '''

    if setup == None:
        setup = XPConstants()
    if instrument == "bp":
        a, b     = setup.aBP, setup.bBP
        LSF = setup.LSFBP[:,:nmax].copy()
    elif instrument == "rp":
        a, b     = setup.aRP, setup.bRP
        LSF = setup.LSFRP[:,:nmax].copy()

    if scale_lsf:
        # print("Scaling LSF")
        LSF = LSF/a/a

    if nmax + k + l > setup.IntsH.shape[0]:
        raise ValueError("nmax + k + l > IntegralsH coefficients. Decrease nmax or l.")


    if k == 0:
        D = np.diag(np.ones(nmax + l))
    elif k == 1:
        D = setup.D1[0:(nmax + l + k), 0:(nmax + l + k)]
    elif k == 2:
        D = setup.D2[0:(nmax + l + k), 0:(nmax + l + k)]
    elif k == 3:
        D = setup.D3[0:(nmax + l + k), 0:(nmax + l + k)]
    elif k == 4:
        D = setup.D4[0:(nmax + l + k), 0:(nmax + l + k)]
    
    if l == 0:
        P = np.diag(np.ones(nmax + k))
    else:
        P = setup.P[0:(nmax + k + l), 0:(nmax + k + l)]
        P = P - np.diag(np.ones(nmax + k + l))*((u0 - b)/a)
        if l > 1:
            P = np.linalg.matrix_power(P, l)
    
    Phi = (1/np.sqrt(a))*math_tools.HermiteFunction(np.array([ (u0-b) / a ]), n).ravel()
    tmp = np.dot(LSF.T, Phi.T)
    tmp = np.concatenate((tmp, np.zeros(k + l)))

    # print(tmp.shape, D.shape, P.shape, np.dot(P, np.dot(D, tmp)).shape, setup.IntsH[:nmax + k + l].shape)
    LKL = ((-1)**k)*np.dot(setup.IntsH[:nmax + k + l], np.dot(P, np.dot(D, tmp)))*np.sqrt(a)*(a**(l-k))
    return LKL
    

def make_L_matrix(u0, k = 2, setup = None, instrument = "bp", n = 55, nmax = 100, scale_lsf = False):
    '''
    # Computes the matrix whose elements are the integrals ∫ L^(k) [u-u0]^l du
    # Inputs:
    # L - the LSF developed in Hermite functions (output of developLSF())
    # u0 - the sample position for which to evaluate the integrals
    # HermiteTransformationMatrices - the matrices required for transformations (saved as RData)
    # k - highest derivative / exponent to be used (default: 2, i.e. L is 3x3 matrix)
    # Output:
    # LMatrix. See eq. 57, 58, 59 in Weiler+2023
    '''

    # Diagonal Elements

    LM = np.diag(np.ones(k + 1))*get_LKL_elements(u0, 0, 0, setup = setup, instrument = instrument, n = n, nmax = nmax, scale_lsf = scale_lsf)
    

    for l in range(1, k + 1):
        LM[0, l] = get_LKL_elements(u0, 0, l, setup = setup, instrument = instrument, n = n, nmax = nmax, scale_lsf = scale_lsf) / factorial(l, exact=True)
    
    # fill the secondary diagonal
        
    if k > 1:
        for l in range(1, k):
            LM[l, l + 1:k+1] = LM[l-1, l:k]

    return LM



def get_R_prod_S(u0, coeff, cov, setup = None, instrument = "bp", k = 2, n = 55, filter = None, scale_lsf = False):

    '''
    # Computes the product of response times SPD in Taylor approximation
    # This version includes the computation of the errors. See Vol. IX, p. 92
    # Inputs:
    # u0 - the sample position
    # L - the development of the LSF in Hermite functions
    # HermiteTransformationMatrices - the list of transformation matrices, incl. D1,D2,D3,D4,H,i
    # c - the vector of coefficients of the source in Hermite functions (continuum approximation)
    # cov - the covariance matrix of c
    # instrument - the instrument ("BP" or "RP", needed for the Hermite basis configuration only)
    # setup - the configuration of Hermite basis functions
    # k - the order of the approximation in the deconvolution (default: 2)
    '''

    if setup == None:
        setup = XPConstants()
    if instrument == "bp":
        a, b     = setup.aBP, setup.bBP
    elif instrument == "rp":
        a, b     = setup.aRP, setup.bRP
    
    H = np.zeros((k+1, n+4))
    tmp = math_tools.HermiteFunction(np.array([ (u0-b) / a ]), n+4)

    if k == 0:
        S = np.dot(tmp[:, :n], coeff)
        covS = np.dot(tmp[:, :n], np.dot(cov, tmp[:, :n].T))
    else:
        H[0, :] = tmp
        if k > 0:
            H[1, :] = np.dot(tmp, setup.D1[0:(n+4), 0:(n+4)]) / a
            if k > 1:
                H[2, :] = np.dot(tmp, setup.D2[0:(n+4), 0:(n+4)]) / (a*a)
                if k > 2:
                    H[3, :] = np.dot(tmp, setup.D3[0:(n+4), 0:(n+4)]) / (a*a*a)
                    if k > 3:
                        H[4, :] = np.dot(tmp, setup.D4[0:(n+4), 0:(n+4)]) / (a*a*a*a)
    

    f = np.dot(H, np.concatenate((coeff, np.zeros(4))))

    cov_pad = np.zeros((n+4, n+4))
    cov_pad[:n, :n] = cov
    covf = np.dot(H, np.dot(cov_pad, H.T))

    LM = make_L_matrix(u0, k=k, setup=setup, instrument=instrument, n=n, scale_lsf = scale_lsf)*a

    if filter is None:
        LM = np.linalg.inv(LM)   # Compute the inverse of the matrix
    else:
        sv = np.linalg.svd(LM)
        d = sv[1] / max(sv[1])
        SI = 1 / sv[1]
        SI[np.where(d < filter)] = 0
        LM = np.dot(np.dot(sv[0], np.diag(SI)), sv[2])

    S = np.dot(LM, f)
    covS = np.dot(LM, np.dot(covf, LM.T))

    return {"u":    u0,
            "S":    S,
            "sigS": np.sqrt(np.diag(covS)),
            "f":    f,
            "LH":   np.dot(LM, H)}




def process_data(data_table):
    """
    Process the data table by converting coefficients etc. columns into numpy arrays.

    Args:
        data_table (pandas.DataFrame): The input data table.

    Returns:
        pandas.DataFrame: The processed data table.

    Raises:
        None

    """
    filters = ['bp', 'rp']

    try:
        for filter in filters:
            data_table[filter + '_coefficients'] = data_table[filter + '_coefficients'].apply(lambda x: np.array(ast.literal_eval(x)))
            data_table[filter + '_coefficient_errors'] = data_table[filter + '_coefficient_errors'].apply(lambda x: np.array(ast.literal_eval(x)))
            data_table[filter + '_coefficient_correlations'] = data_table[filter + '_coefficient_correlations'].apply(lambda x: np.array(ast.literal_eval(x)))
    except:
        print("Data already processed")
    return data_table


def req_cols_in_table(data_table, required_columns = ['source_id', 'bp_coefficients', 'rp_coefficients',
                                              'bp_coefficient_errors', 'rp_coefficient_errors',
                                              'bp_coefficient_correlations', 'rp_coefficient_correlations']):
    
    """
    Validate that a table-like object contains the required column names.

    Parameters
    ----------
    data_table : object
        Table-like object that exposes a .columns attribute (for example, a pandas.DataFrame).
    required_columns : list of str, optional
        Iterable of column names to check for. Defaults to
        ['source_id', 'bp_coefficients', 'rp_coefficients',
            'bp_coefficient_correlations', 'rp_coefficient_correlations'].

    Returns
    -------
    bool
        True if all required column names are present in data_table.columns, False otherwise.

    Side effects
    ------------
    If any required columns are missing, their names are printed to standard output.

    Notes
    -----
    - The function performs simple membership checks against data_table.columns and does not modify
        the input object.
    - data_table.columns should be an iterable of strings (e.g., pandas.Index).
    """

    missing_columns = [col for col in required_columns if col not in data_table.columns]
    if missing_columns:
        print(f"Missing columns in data table: {missing_columns}")
        return False
    return True


def download_xp_spectra_if_needed(source_id_table, data_release='Gaia DR3',
                        source_id_column='source_id',
                        gaia_class=None,
                        retrieval_type='XP_CONTINUOUS',
                        format_type='csv',
                        data_structure='RAW', output_file = 'xp_continuous_downloaded.csv'):
    """
    Download and prepare XP spectra for a set of Gaia source IDs if needed.
    This function checks whether the provided source_id_table already contains the
    required columns for XP spectra retrieval (via req_cols_in_table). If the table
    does not contain the required columns, it will request XP spectra using the
    download_xp_spectra.download_xp_spectra helper, save the raw download to
    output_file (when applicable), and then run the result through process_data.
    If the required columns are present, the function will operate on a copy of
    the provided table and call process_data before returning.
    Parameters
    ----------
    source_id_table : table-like
        A table-like object (for example a pandas.DataFrame) that contains Gaia
        source identifiers. The function will inspect this table to decide whether
        a download is necessary.
    data_release : str, optional
        Gaia data release to use for retrieval (default: 'Gaia DR3').
    source_id_column : str, optional
        Name of the column in source_id_table that contains the Gaia source IDs
        (default: 'source_id').
    gaia_class : str or None, optional
        Optional Gaia object class filter to pass through to the downloader
        (default: None).
    retrieval_type : str, optional
        The retrieval type argument passed to the downloader (default:
        'XP_CONTINUOUS').
    format_type : str, optional
        The file/format type requested from the downloader (default: 'csv').
    data_structure : str, optional
        The data structure argument passed to the downloader (default: 'RAW').
    output_file : str, optional
        Filepath where downloaded data will be saved when a download occurs
        (default: '../Data/xp_continuous_downloaded.csv').
    Returns
    -------
    pandas.DataFrame
        A processed copy of the datalink table. If a download was necessary, this
        will be the processed result of the downloaded data; otherwise it will be
        the processed copy of the original source_id_table.
    """
    if not req_cols_in_table(source_id_table):
        datalink = download_xp_spectra.download_xp_spectra(source_id_table, data_release=data_release,
                             source_id_column=source_id_column,
                             gaia_class=gaia_class,
                             retrieval_type=retrieval_type,
                             format_type=format_type,
                             data_structure=data_structure,
                             output_file=output_file)
    else:
        datalink = source_id_table.copy()
    datalink = process_data(datalink)
    return datalink