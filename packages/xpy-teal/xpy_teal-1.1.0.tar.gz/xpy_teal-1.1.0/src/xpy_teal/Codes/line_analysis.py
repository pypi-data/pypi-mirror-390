######################################
#
#   xp_spectral_lines/line_analysis_tools.py
#
# Tools translated from Michael Weiler's original R code
# For details of the formalism refer to 
#     https://ui.adsabs.harvard.edu/abs/2023A%26A...671A..52W/abstract
# 
# This implementation:
#     Sagar Malhotra under supervision of Michael Weiler and Friedrich Anders (ICCUB, 2024)
#
######################################
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


import numpy as np
from scipy.linalg import eigvals, svd
import pandas as pd
from joblib import Parallel, delayed
import time
from itertools import chain
from . import math_tools, spectrum_tools

def getRoots(coef, cov,setup=None, n=None, small=1E-7, conditioning=False):
    """
    Computes the roots and their errors for a linear combination of Hermite functions.
    
    # Inputs:
      coef - the coefficients of the linear combination
      cov  - the covariance matrix for coef
    
    # Optional inputs:
      setup - list with transformation matrices: HermiteTransfromationMatrices.RData
      small - limit on the relative absolute value of the imaginary part that is tolerated (default: 1E-7)
      conditioning - if TRUE, the condition numbers of the roots are also provided.
    
    # Output 
      dictionary including all roots, and the real roots and their errors.
    """
    if n is None:
        n = len(coef) - 1

    if setup is None:
        # load from disk if not provided
        setup = spectrum_tools.XPConstants()

    
    # the non-standard companion matrix (eq. 26):
    B         = setup.RootsH[:n,:n].copy()
    
    B[:, -1]  = B[:, -1] - np.sqrt(n/2) * coef[:-1] / coef[-1]  # exchange the last column
    # the roots as eigenvalues of B:
    # print(B)
    roots     = eigvals(B)
    # select real roots:
    d         = np.where(abs(np.imag(roots)) / abs(np.real(roots)) < small)[0]
    realRoots = np.real(roots[d])
    nReal     = len(d)

    # compute the covariance matrix of the real roots in linear approximation:
    Hermite = np.matmul(np.matmul(math_tools.HermiteFunction(realRoots, n+2), 
                                  setup.D1[0:n+2, 0:n+2]), np.concatenate((coef, [0])))

    # compute the condition numbers of the roots if requested:
    if conditioning and nReal > 0:
        # left eigenvectors:
        LE  = math_tools.HermiteFunction(realRoots, nReal)
        # right eigenvectors:
        sv  = svd(LE)
        tmp = 1. / sv[1]
        tmp[np.where(sv[1] < 1E-12 * max(sv[1]))] = 0
        RE  = sv[2].T @ np.diag(tmp) @ sv[0].T
        condition = np.abs(np.array([np.inner(LE[:,i], RE[:,i]) / 
                                     (np.sqrt(np.inner(LE[:,i], LE[:,i])) * 
                                      np.sqrt(np.inner(RE[:,i], RE[:,i]))) for i in range(nReal)]))
    else:
        condition = None

    if nReal == 1:
        J = -1/Hermite * math_tools.HermiteFunction(realRoots, n=n+1)
    else:
        J = -np.diag(1/Hermite) @ math_tools.HermiteFunction(realRoots, n=n+1)
    J = np.real(J)
    err = J @ cov[0:n+1, 0:n+1] @ J.T

    return {"roots": roots, 
            "realRoots": realRoots, 
            "sigma": np.sqrt(np.diag(err)), 
            "cov": err, 
            "condition": condition}


def getLocalExtrema(coef, cov, setup=None, conditioning=False):
    """
    Computes the positions and their uncertainties of local minima and maxima
    in a linear combination of Hermite functions.
    
    # Inputs:
      coef - the coefficients of the linear combination
      cov - the covariance matrix of coef
    
    # Optional inputs:
      setup: list with the required matrices for the zero and first derivatives
                    (computed with getDerivativeMatrices())
      conditioning - if TRUE, the condition numbers of the real roots are also computed.
                     Much slower computation than without.

    # Output 
      dictionary including all computed information
    """
    n = len(coef)
    
    if setup is None:
        setup = spectrum_tools.XPConstants()

    coef1 = np.matmul(setup.D1[0:n+1, 0:n+1], np.concatenate([coef, [0]]))
    cov1  = np.matmul(setup.D1[0:n+1, 0:n+1], 
                      np.vstack([np.hstack([cov, np.zeros((n, 1))]), 
                                 np.zeros((1, n+1))])) @ np.transpose(setup.D1[0:n+1, 0:n+1])
    cov2  = np.zeros((n+2, n+2))
    cov2[:n, :n] = cov

    roots = getRoots(coef1, cov1, setup=setup, conditioning=conditioning)

    # computing the values and errors of the second derivative at the roots:
    M = np.matmul(math_tools.HermiteFunction(roots['realRoots'], n+2), setup.D2[0:n+2, 0:n+2])
    v = np.matmul(M, np.concatenate([coef, [0, 0]]))
    E = np.matmul(np.matmul(M, cov2), np.transpose(M))

    kind = np.repeat("minimum", len(roots['realRoots']))
    kind[np.where(v < 0)] = "maximum"

    return {'location':   roots['realRoots'], 
            'error':      roots['sigma'], 
            'cov':        roots['cov'], 
            'condition':  roots['condition'], 
            'kind':       kind,
            'secondDerivativeAtRoots':        v, 
            'ErrorOnSecondDerivativeAtRoots': np.sqrt(np.diag(E)), 
            'CovForSecondDerivatives':        E, 
            'roots':      roots}

def getInflectionPoints(coef, cov, setup=None, conditioning=False):
    """
    Computes the positions and their uncertainties of inflection points
    in a linear combination of Hermite functions.
    
    # Inputs:
    coef - the coefficients of the linear combination
    cov - the covariance matrix of coef
    
    # Optional inputs:
    setup: list with the required matrices for the zero and first derivatives
           (computed with getDerivativeMatrices())
    conditioning - if TRUE, the condition numbers of the real roots are also computed.
                   Much slower computation than without.

    # Output 
      dictionary including all computed information
    """
    n = len(coef)
    if setup is None:
        # use the pre-defined HermiteTransformationMatrices from RData file
        # (assuming the file is saved in the same directory as this script)
        setup = spectrum_tools.XPConstants()

    coef1 = setup.D2[:(n+2), :(n+2)].dot(np.append(coef, [0, 0]))
    cov1  = setup.D2[:(n+2), :(n+2)].dot(
            np.block([[cov, np.zeros((n, 2))], [np.zeros((2, n+2))]])).dot(
            setup.D2[:(n+2), :(n+2)].T)
    cov2  = np.zeros((n+3, n+3))
    cov2[:n, :n] = cov

    roots = getRoots(coef1, cov1, setup=setup, conditioning=conditioning)

    # computing the values and errors of the third derivative at the roots:
    M = math_tools.HermiteFunction(roots["realRoots"], n+3).dot(setup.D3[:(n+3), :(n+3)])
    v = M.dot(np.append(coef, [0, 0, 0]))
    E = M.dot(cov2).dot(M.T)

    kind = np.repeat("increasing", len(roots["realRoots"]))
    kind[v < 0] = "decreasing"

    return {"location":   roots["realRoots"],
            "error":      roots["sigma"],
            "covariance": roots["cov"],
            "condition":  roots["condition"],
            "kind":       kind,
            "thirdDerivativeAtRoots":        v,
            "ErrorOnThirdDerivativeAtRoots": np.sqrt(np.diag(E)),
            "CovForThirdDerivatives":        E,
            "roots":      roots}


def getLinesInNDeriv(coefIn, covIn, N=0, instrument="none", setup=None):
    """
    Extracts the basic line parameters. 
    First it converts the input to its N-th derivative.
    
    # Output:
      Dictionary of extrema positions, errors on the extrema positions, 
                    the S/N for the second derivatives at the positions 
                    of the extrema, and the p-value of the extrema. 
    """
    n = len(coefIn)

    if setup is None:
        setup = spectrum_tools.XPConstants()
    if instrument == "bp":
        a = setup.aBP
        b = setup.bBP
    elif instrument == "rp":
        a = setup.aRP
        b = setup.bRP
    else:
        print("Warning: You are using getLinesInNDeriv without specifying the instrument - no scaling is applied")
        a = 1
        b = 0
    
    
    coefPad = np.concatenate((coefIn, np.zeros(N)))
    covPad  = np.zeros((n + N, n + N))
    covPad[:n, :n] = covIn

    if N == 0:
        coef   = coefIn
        cov    = covIn
    else:
        if N == 1:
            Transf = setup.D1[:n + N, :n + N]
        elif N == 2:
            Transf = setup.D2[:n + N, :n + N]
        elif N == 3:
            Transf = setup.D3[:n + N, :n + N]
        else:
            raise ValueError("N too high. Don't be stupid.")
        coef   = np.dot(Transf, coefPad)
        cov    = np.dot(np.dot(Transf, covPad), Transf.T)

    e = getLocalExtrema(coef, cov, setup=setup)
    p = e["location"] * a + b
    x = e["secondDerivativeAtRoots"] / e["ErrorOnSecondDerivativeAtRoots"]
    signif = 1 - np.exp(-x*x / 2)

    inf = getInflectionPoints(coef, cov, setup=setup)
    pinf = inf["location"] * a + b
    xinf = inf["thirdDerivativeAtRoots"] / inf["ErrorOnThirdDerivativeAtRoots"]
    signifInf = 1 - np.exp(-xinf*xinf / 2)

    # print('instrument:', instrument)
    # print(pinf, p)
    widths = [np.min(pinf[pi < pinf]) - np.max(pinf[pi > pinf]) for pi in p]
    widthsError = [np.sqrt(inf["covariance"][np.where(pinf == min(pinf[pi > pinf]))[0][0], 
                                             np.where(pinf == min(pinf[pi > pinf]))[0][0]] + 
                           inf["covariance"][np.where(pinf == max(pinf[pi < pinf]))[0][0], 
                                             np.where(pinf == max(pinf[pi < pinf]))[0][0]] -
                           2 * inf["covariance"][np.where(pinf == min(pinf[pi > pinf]))[0][0], 
                                                 np.where(pinf == max(pinf[pi < pinf]))[0][0]])
                   for pi in p]

    res = {"estimLinePos":   p, 
           "estimLineErr":   e["error"] * a, 
           "SNonSecondDerivative": x, 
           "estimSignif":    signif,
           "lineWidths":     widths, 
           "lineWidthsError":                widthsError, 
           "secondDerivativeAtRoots":        e["secondDerivativeAtRoots"] / a**(N+2),
           'ErrorOnSecondDerivativeAtRoots': e['ErrorOnSecondDerivativeAtRoots']/a**(N+2),
           'CovForSecondDerivatives':        e['CovForSecondDerivatives']/a**(2*N+4),
           'kind':           e['kind'],
           'estimInfPos':    pinf, 
           'estimInfErr':    inf['error']*a, 
           'estimInfCov':    inf['covariance']*a*a, 
           'estimInfSignif': signifInf, 
           'infKind':        inf['kind']}
    return res

def getLinesInDeriv_parallel(datalink, n_cores=2, batch_size=None):
    '''
    Perform parallel processing to get the extrema in 0 and 2nd derivative
    for each source_id in the datalink.

    Parameters:
    - datalink: pandas DataFrame
        The input data containing the spectra information.
    - n_cores: int, optional
        The number of CPU cores to be used for parallel processing. Default is 2.
    - batch_size: int, optional
        The number of spectra to be processed in each batch. Default is None.

    Returns:
    - pandas DataFrame
        A DataFrame containing the extrema in 0 and 2nd derivative for each source_id.
    '''

    setup = spectrum_tools.XPConstants()
    if batch_size is None:
        batch_size = len(datalink)//n_cores

    def getLinesInDeriv_single(step, batch_size):
        '''
        Helper function to get the extrema in 0 and 2nd derivative for a single batch of spectra.

        Parameters:
        - step: int
            The step number of the current batch.
        - batch_size: int
            The number of spectra to be processed in each batch.

        Returns:
        - list
            A list of dictionaries containing the extrema in 0 and 2nd derivative for each source_id.
        '''

        line_dict_list = []

        for i in range(step * batch_size, min((step + 1) * batch_size, len(datalink))):
            spectrum = spectrum_tools.XP_Spectrum(datalink.iloc[i], setup=setup)

            for order in [0, 2]:
                bp_dict = getLinesInNDeriv(spectrum.BP, spectrum.BP_cov, N=order, instrument="bp", setup=setup)
                rp_dict = getLinesInNDeriv(spectrum.RP, spectrum.RP_cov, N=order, instrument="rp", setup=setup)

                line_dict = {'BP': bp_dict, 'RP': rp_dict, 'source_id': datalink.iloc[i]['source_id'], 'N': order}
                line_dict_list.append(line_dict)


        return line_dict_list

    max_step = int(np.ceil(len(datalink) / batch_size))
    # merge all the dictionaries into a single dictionary from parallel processing
    results = Parallel(n_jobs=n_cores)(delayed(getLinesInDeriv_single)(step, batch_size) for step in range(max_step))
    results = list(chain.from_iterable(results))

    return pd.DataFrame(results)


def getNarrowLineUpperLimit(spectrum, uLine, instrument = 'bp', setup = None, k = 2, Q = 1.0, n = 55,
                             nmax = 100, scale_lsf = True, disp_inverse = False):
    '''
    #Inputs:
    spectrum - bp or rp coefficients and covariances
    uLine - the line position in pseudo-wavelength
    instrument - 'bp' or 'rp'
    setup - XPConstants
    k - the order of approximation for continuum deconvolution (default: 2)
    Q - Quantile for the upper limit (default: 1.0)
    '''

    if setup is None:
        setup = spectrum_tools.XPConstants()
    if instrument == 'bp':
        coef = spectrum.BP
        cov = spectrum.BP_cov
        a = setup.aBP
        b = setup.bBP
        LSF = setup.LSFBP[:,:nmax].copy()
    elif instrument == 'rp':
        coef = spectrum.RP
        cov = spectrum.RP_cov
        a = setup.aRP
        b = setup.bRP
        LSF = setup.LSFRP[:,:nmax].copy()
    
    uL = uLine
    H   = math_tools.HermiteFunction(np.array([ (uL-b) / a ]), nmax).ravel()
    lsf = np.dot(H, LSF.T)

    NF = np.dot(setup.IntsH[:n], lsf)*a
    lsf = lsf / NF

    D = np.sqrt(np.dot(np.dot(lsf.T, np.linalg.inv(cov)), lsf))

    Rs = spectrum_tools.get_R_prod_S(uL, coef, cov, setup=setup, instrument=instrument,
                                      k = k, n=n, scale_lsf=scale_lsf)

    W = abs(Q / (Rs['S'][0] * D) * abs(spectrum_tools.disp_derivative(uL, order=1, 
                                            instrument=instrument, setup=setup, disp_inverse=disp_inverse)))

    return {'upperLimit': W, 'Q': Q}



def getNarrowLineEquivalentWidth(spectrum, line_dict, specific_lines = None, instrument = 'bp', setup = None, k = 2,
                                  uLine = None, n = 55, nmax = 100, scale_lsf = True, disp_inverse = False):
    '''
    #Inputs:
    spectrum - bp or rp coefficients and covariances
    line_dict - the dictionary containing the extrema information
    specific_lines - a list of index of lines to compute the equivalent width for
    instrument - 'bp' or 'rp'
    setup - XPConstants
    k - the order of approximation for continuum deconvolution (default: 2)
    uLine - a priori line position in pseudo-wavelength
    '''

    if setup is None:
        setup = spectrum_tools.XPConstants()
    if instrument == 'bp':
        coef = spectrum.BP
        cov = spectrum.BP_cov
        a = setup.aBP
        b = setup.bBP
        LSF = setup.LSFBP[:,:nmax].copy()
    elif instrument == 'rp':
        coef = spectrum.RP
        cov = spectrum.RP_cov
        a = setup.aRP
        b = setup.bRP
        LSF = setup.LSFRP[:,:nmax].copy()


    # Check if the order is 0
    # if len(line_df[line_df['N'] != 0]) > 0:
    #     raise ValueError('The order of the lines is not 0')

    if uLine is None:
        uL = line_dict[instrument.upper()].values[0]['estimLinePos'][specific_lines[0]]
    else:
        uL = uLine
    eror_u0 = line_dict[instrument.upper()].values[0]['estimLineErr'][specific_lines[0]]


    H   = math_tools.HermiteFunction(np.array([ (uL-b) / a ]), nmax).ravel() #
    
    # print(LSF.shape)
    lsf = np.dot(H, LSF.T)

    # Normalization factor
    NF = np.dot(setup.IntsH[:n], lsf)*a
    lsf = lsf / NF
    
    # print(lsf)

    H   = math_tools.HermiteFunction(np.array([ (uL-b) / a ]), n + 2).ravel()
    # Second derivative at the line position
    M = np.dot(H[:n + 2], setup.D2[:n + 2, :n + 2]) /(a**2)
    # print(M)
    L2 = M @ np.concatenate((lsf, np.zeros(2)))

    v = np.dot(M, np.concatenate((coef, np.zeros(2))))
    err1 = M.flatten()
    ratio = v / L2

    # print('Ratio for ', uL, ' = ', ratio)
    coefCont = coef - ratio * lsf

    Rs = spectrum_tools.get_R_prod_S(uL, coefCont, cov, instrument=instrument, setup=setup, k=k, n = n, scale_lsf=scale_lsf)

    W = ratio / Rs['S'][0] * np.abs(spectrum_tools.disp_derivative(uL, order=1, instrument=instrument, setup=setup, disp_inverse=disp_inverse))

    J = np.dot(np.abs(spectrum_tools.disp_derivative(uL, order=1, instrument=instrument, setup=setup, disp_inverse = disp_inverse)) / L2, (err1[:n] / Rs['S'][0] - v / Rs['S'][0] / Rs['S'][0] * (Rs['LH'][0, :n] - np.dot(Rs['LH'][0, :n], lsf) * err1[:n] / L2)))
    errW = np.sqrt(np.dot(np.dot(J, cov), J.T))

    temp_dict = {'W': W, 'errW': errW, 'u0': uL, 'u0err': eror_u0}
    return temp_dict


def getNarrowLineEquivalentWidthSecondOrder(spectrum, line_dict, specific_lines = None, instrument = 'bp',
                                             setup = None, k = 2, uLine = None, n = 55, nmax = 100, scale_lsf = True, disp_inverse = False):
    '''
    #Inputs:
    spectrum - bp or rp coefficients and covariances
    line_dict - the dictionary containing the extrema information
    specific_lines - a list of index of lines to compute the equivalent width for
    instrument - 'bp' or 'rp'
    setup - XPConstants
    k - the order of approximation for continuum deconvolution (default: 2)
    uLine - a priori line position in pseudo-wavelength
    '''

    if setup is None:
        setup = spectrum_tools.XPConstants()
    if instrument == 'bp':
        coef = spectrum.BP
        cov = spectrum.BP_cov
        a = setup.aBP
        b = setup.bBP
        LSF = setup.LSFBP[:,:nmax].copy()
    elif instrument == 'rp':
        coef = spectrum.RP
        cov = spectrum.RP_cov
        a = setup.aRP
        b = setup.bRP
        LSF = setup.LSFRP[:,:nmax].copy()

    
    # # Check if the order is 2
    # if len(line_df[line_df['N'] != 2]) > 0:
    #     raise ValueError('The order of the lines is not 2')

    if uLine is None:
        uL = line_dict[instrument.upper()].values[0]['estimLinePos'][specific_lines[0]]
    else:
        uL = uLine
    eror_u0 = line_dict[instrument.upper()].values[0]['estimLineErr'][specific_lines[0]]


    H   = math_tools.HermiteFunction(np.array([ (uL-b) / a ]), nmax).ravel() #
    lsf = np.dot(H, LSF.T)

    # Normalization factor
    NF = np.dot(setup.IntsH[:n], lsf)*a
    lsf = lsf / NF

    H   = math_tools.HermiteFunction(np.array([ (uL-b) / a ]), n + 4).ravel()

    # Second derivative at the line position
    M = np.dot(H[:n + 4], setup.D4[:n + 4, :n + 4]) /(a**4)
    L4 = M @ np.concatenate((lsf, np.zeros(4)))

    v = np.dot(M, np.concatenate((coef, np.zeros(4))))
    err1 = M.flatten()
    ratio = v / L4

    # print('Ratio for ', uL, ' = ', ratio)

    coefCont = coef - ratio * lsf

    Rs = spectrum_tools.get_R_prod_S(uL, coefCont, cov, instrument=instrument, setup=setup, k=k, n = n, scale_lsf=scale_lsf)

    W = ratio / Rs['S'][0] * np.abs(spectrum_tools.disp_derivative(uL, order=1, instrument=instrument, setup=setup, disp_inverse=disp_inverse))

    J = np.dot(np.abs(spectrum_tools.disp_derivative(uL, order=1, instrument=instrument, setup=setup, disp_inverse=disp_inverse)) / L4, (err1[:n] / Rs['S'][0] - v / Rs['S'][0] / Rs['S'][0] * (Rs['LH'][0, :n] - np.dot(Rs['LH'][0, :n], lsf) * err1[:n] / L4)))
    errW = np.sqrt(np.dot(np.dot(J, cov), J.T))


    temp_dict = {'W': W, 'errW': errW, 'u0': uL, 'u0err': eror_u0}
    return temp_dict



def hydrogen_series(n1, n2):
    """
    Calculates the wavelength of the spectral line in the hydrogen series
    corresponding to the given energy levels.

    Args:
        n1 (int): The final energy level.
        n2 (int): The initial energy level.

    Returns:
        float: The wavelength of the spectral line in nm.

    Raises:
        None

    """
    if n2 < n1:
        print('n2 must be greater than n1')
        return None
    else:
        RH = 1.09677581*10**7

        wavelength = 1 / (RH * (1/n1**2 - 1/n2**2))
    
        return wavelength*10**9
    
    

def get_default_line_wavelengths(list_of_default_lines):
    """
    Returns a list of wavelengths corresponding to the given list of default lines.

    Args:
        list_of_default_lines (str): A comma-separated string of default line names.

    Returns:
        list: A list of wavelengths corresponding to the given default lines. If a line name does not match, None is assigned.

    """
    lines = list_of_default_lines.split(",")
    
    if lines[0] != "":
        # Initialize an empty list to hold the wavelengths
        wavelengths = []
        
        for line in lines:
            if line == "Halpha":
                wavelengths.append(hydrogen_series(2, 3))
            elif line == "Hbeta":
                wavelengths.append(hydrogen_series(2, 4))
            elif line == "Hgamma":
                wavelengths.append(hydrogen_series(2, 5))
            elif line == "Hdelta":
                wavelengths.append(hydrogen_series(2, 6))
            elif line == "Hepsilon":
                wavelengths.append(hydrogen_series(2, 7))
            else:
                wavelengths.append(None)  # Assign None if the line name does not match
    else:
        wavelengths = []
    
    return wavelengths


def get_list_of_wavelegths(list_of_line_wavelengths):
    """
    Converts a comma-separated string of line wavelengths into a list of floats.

    Args:
        list_of_line_wavelengths (str): A comma-separated string of line wavelengths.

    Returns:
        list: A list of floats representing the line wavelengths.
    """

    lines = list_of_line_wavelengths.split(",")

    if lines[0] != "":
        # Initialize an empty list to hold the wavelengths
        wavelengths = []
        
        for line in lines:
            wavelengths.append(float(line))
    else:
        wavelengths = []
    
    return wavelengths

def getLineNames(default_lines, other_lines):
    """
    Returns a list of line names based on the default lines and other lines provided.

    Parameters:
    default_lines (str): A comma-separated string of default line names.
    other_lines (str): A comma-separated string of other line values.

    Returns:
    list: A list of line names, including the default lines and 
    the rounded other lines until unique names are obtained.
    """
    default_lines = default_lines.split(',')

    other_lines = other_lines.split(',')
    other_lines = [float(i) for i in other_lines]

    temp_line_names = [round(i) for i in other_lines]

    rounding_decimal_places = 1
    while len(np.unique(temp_line_names)) < len(other_lines):
        temp_line_names = [round(i, rounding_decimal_places) for i in other_lines]
        rounding_decimal_places += 1
    
    temp_line_names = ['Line_' + str(i)  + 'nm' for i in temp_line_names]
    temp_line_names = default_lines + temp_line_names

    return temp_line_names

def getDispShift(wavelength, tol = 10**-4):
    """
    Calculates the displacement shift based on the given wavelength.
    (Currently only supports the Halpha line in the hydrogen series.)

    Parameters:
    wavelength (float): The wavelength value to calculate the displacement shift for.
    tol (float, optional): The tolerance value for comparing the wavelength with the hydrogen series. Default is 10**-4.

    Returns:
    float: The displacement shift value.

    """
    shift = 0.0
    if np.abs(wavelength - hydrogen_series(2, 3)) <= tol:
        shift = 0.3
    return shift



def analyse_linedict(temp_source_id, spectrum, uL, line_dict, order, setup, w,
                      instrument='bp', k=2,
                     dispShift=None, nmax=100):
    """
    Analyzes a line dictionary and returns a DataFrame with the analysis results.

    Parameters:
    - temp_source_id (int): The ID of the source.
    - spectrum (array-like): The spectrum data.
    - uL (float): The uncertainty in the line position.
    - line_dict (dict): The line dictionary containing line information.
    - order (int): The order of the extrema.
    - setup (str, optional): The setup used for the analysis. Defaults to None.
    - w (float): LSF width.
    - instrument (str, optional): The instrument used for the analysis. Defaults to 'bp'.
    - k (int, optional): The k value used for the analysis. Defaults to 2.
    - dispShift (float, optional): The shift in psuedowavelength. Defaults to None.
    - nmax (int, optional): The maximum value of n. Defaults to 100.

    Returns:
    - temp_df (DataFrame): The DataFrame containing the analysis results.
    """

    if order == 2:
        higherOrder = True
    else:
        higherOrder = False
    
    # w = spectrum_tools.get_LSF_width(uL, setup=setup, instrument=instrument, order=order)

    LSFwidth = np.sort([w["p1"], w["p2"]])

    # line_dict to line_df
    
    # keys_to_fetch = ['estimLinePos', 'estimLineErr',"estimSignif", "lineWidths"]
    # filtered_dict = dict((key, line_dict[instrument.upper()].values[0][key]) for key in keys_to_fetch)

    # line_df = pd.DataFrame(filtered_dict)
    # line_df['source_id'] = temp_source_id

    # idx = np.where((line_df['estimLinePos'] > LSFwidth[0]) & (line_df['estimLinePos'] < LSFwidth[1]))[0]

    idx = np.where((line_dict[instrument.upper()].values[0]['estimLinePos'] > LSFwidth[0]) & \
                     (line_dict[instrument.upper()].values[0]['estimLinePos'] < LSFwidth[1]))[0]

    hit = len(idx)

    if hit == 1:
        if higherOrder:
            width = getNarrowLineEquivalentWidthSecondOrder(spectrum, line_dict, specific_lines=idx,
                                                            instrument=instrument,
                                                            setup=setup, k=k, uLine=uL, n=55, nmax=nmax,
                                                            scale_lsf=True, disp_inverse=False)


        else:
            width = getNarrowLineEquivalentWidth(spectrum, line_dict, specific_lines=idx, instrument=instrument,
                                                 setup=setup, k=k, uLine=uL, n=55, nmax=nmax,
                                                 scale_lsf=True, disp_inverse=False)
            
        temp_df = pd.DataFrame({'source_id': [temp_source_id],
                                'p': [round(line_dict[instrument.upper()].values[0]["estimSignif"][idx[0]], 6)],
                                'W': width['W'], 'Werror': width['errW'],
                                'ExtremaInRange': [hit],
                                'dispShift': [dispShift],
                                'D': [round(line_dict[instrument.upper()].values[0]['lineWidths'][idx[0]] / w['D'], 6)],
                                'order': [order]})
    else:
        # get upper limit:
        upper_limit = getNarrowLineUpperLimit(spectrum, uL, instrument=instrument, setup=setup, k=k, Q=7.709, 
                                              n=55, nmax=100, scale_lsf=True, disp_inverse=False)
        width = {"W": 0, "errW": upper_limit["upperLimit"]}

         # if hit = 0 or higher than 1, we report the upper limit
        temp_df = pd.DataFrame({'source_id': [temp_source_id], 'p': [np.nan],
                                'W': width['W'], 'Werror': width['errW'],
                                'ExtremaInRange': [hit],
                                'dispShift': [dispShift], 'D': [np.nan], 'order': ['UL']})
        

    return temp_df




def analyseLine_singlelambda(datalink, wavelength, LINE_DICT, setup=None, k=2, 
                             dispShift=None, order_by_user=None, nmax=100, ncores=2,
                             batch_size=None):
    """
    Analyzes a single line at a given wavelength in the XP Spectra dataset.

    Args:
        datalink (pandas.DataFrame): The dataset containing the XP Spectra.
        wavelength (float): The wavelength of the line to be analyzed.
        LINE_DICT (pandas.DataFrame): The dictionary containing extrema position information.
        setup (spectrum_tools.XPConstants, optional): The setup configuration. Defaults to None.
        k (int, optional): The number of nearest neighbors to consider. Defaults to 2.
        dispShift (float, optional): The shift in psuedowavelength. Defaults to None.
        order_by_user (int, optional): The order of the line specified by the user. Defaults to None.
        nmax (int, optional): The maximum number of lines to analyze. Defaults to 100.
        ncores (int, optional): The number of CPU cores to use for parallel processing. Defaults to 2.
        batch_size (int, optional): The batch size for parallel processing. Defaults to None.

    Returns:
        pandas.DataFrame: The result of the line analysis.
    """

    if setup is None:
        setup = spectrum_tools.XPConstants()

    if wavelength < 650:
        instrument = "bp"
    else:
        instrument = "rp"

    if dispShift is None:
        dispShift = getDispShift(wavelength)

    if batch_size is None:
        batch_size = len(datalink)//ncores

    uL = spectrum_tools.disp_u_to_lambda(wavelength, instrument=instrument, setup=setup, disp_inverse=True) + dispShift  # nominal position of the line in pseudo-wavelength

    w_0 = spectrum_tools.get_LSF_width(uL, setup=setup, instrument=instrument, order=0)
    w_2 = spectrum_tools.get_LSF_width(uL, setup=setup, instrument=instrument, order=2)

    LSF_WIDTH_LIST = [w_0, w_2]


    def analyseLine_singlelambda_parallel(step, batch_size, datalink, uL, LINE_DICT, setup, LSF_WIDTH_LIST,  
                                          instrument, k, dispShift, order_by_user, nmax):
        """
        Performs line analysis in parallel for a given batch of data.

        Args:
            step (int): The step index for parallel processing.
            batch_size (int): The batch size for parallel processing.
            datalink (pandas.DataFrame): The dataset containing the XP Spectra.
            uL (float): The nominal position of the line in pseudo-wavelength.
            LINE_DICT (pandas.DataFrame): The dictionary containing extrema position information.
            setup (spectrum_tools.XPConstants): The setup configuration.
            LSF_WIDTH_LIST (list): A list of LSF widths for different orders.
            instrument (str): The instrument type.
            k (int): The number of nearest neighbors to consider.
            dispShift (float): The shift in psuedowavelength.
            order_by_user (int): The order of the line specified by the user.
            nmax (int): The maximum number of lines to analyze.

        Returns:
            pandas.DataFrame: The result of the line analysis for the given batch.
        """

        TEMP_DF = pd.DataFrame()
        for i in range(step*batch_size, min((step+1)*batch_size, len(datalink))):
            spectrum = spectrum_tools.XP_Spectrum(datalink.iloc[i], setup=setup)
            temp_source_id = datalink.iloc[i]['source_id']

            if order_by_user is None:
                ORDER = [0, 2]
                for order_index in range(len(ORDER)):
                    temp_lsf_width = LSF_WIDTH_LIST[order_index]

                    order = ORDER[order_index]
                    
                    line_dict = LINE_DICT[(LINE_DICT['source_id'] == temp_source_id) & (LINE_DICT['N'] == order)].copy()
                    
                    temp_df = analyse_linedict(temp_source_id, spectrum, uL, line_dict, order=order,
                                                        setup=setup, instrument=instrument, k=k,
                                                        dispShift=dispShift, nmax=nmax,
                                                        w=temp_lsf_width)
                    
                    TEMP_DF = pd.concat([TEMP_DF, temp_df], ignore_index=True)


                    # Needs to be changed if the priority order of selecting rows 
                    # from the final result is changed
                    
                    if order_index == 0:
                        if temp_df['ExtremaInRange'].values[0] == 1:
                            break



            else:
                line_dict = LINE_DICT[(LINE_DICT['source_id'] == temp_source_id) & (LINE_DICT['N'] == order_by_user)].copy()
                temp_df = analyse_linedict(temp_source_id, spectrum, uL, line_dict, order=order_by_user,
                                                    setup=setup, instrument=instrument, k=k,
                                                    dispShift=dispShift, nmax=nmax,
                                                    w=LSF_WIDTH_LIST[order_by_user])
                
                TEMP_DF = pd.concat([TEMP_DF, temp_df], ignore_index=True)

        return TEMP_DF

    # Parallel processing

    max_step = int(np.ceil(len(datalink)/batch_size))
    results = Parallel(n_jobs=ncores)(delayed(analyseLine_singlelambda_parallel)(step, batch_size, 
                                                                                datalink, uL, LINE_DICT, setup,
                                                                                LSF_WIDTH_LIST, 
                                                                                instrument, k, dispShift, 
                                                                                order_by_user,
                                                                                nmax) for step in range(max_step))             
    
    result = pd.concat(results, ignore_index=True)

    return result


def analyseLine_all_wavelengths(datalink, WAVELENGTH_LIST, LINE_NAMES, LINE_DICT, setup=None, k=2,
                                dispShift=None, order_by_user=None, nmax=100, ncores=2,
                                batch_size=None):
    """
    Analyzes spectral lines for all wavelengths in the given list.

    Args:
        datalink (str): The data link.
        WAVELENGTH_LIST (list): A list of wavelengths to analyze.
        LINE_NAMES (list): A list of names corresponding to the spectral lines.
        LINE_DICT (dict): A dictionary containing information about extrema position.
        setup (object, optional): The setup object. Defaults to None.
        k (int, optional): The value of k. Defaults to 2.
        dispShift (float, optional): The shift in psuedowavelength. Defaults to None.
        order_by_user (str, optional): The order specified by the user. Defaults to None.
        nmax (int, optional): The maximum number of iterations. Defaults to 100.
        ncores (int, optional): The number of cores to use. Defaults to 2.
        batch_size (int, optional): The batch size. Defaults to None.

    Returns:
        pandas.DataFrame: The result of the analysis.
    """

    if setup is None:
        setup = spectrum_tools.XPConstants()

    if batch_size is None:
        batch_size = len(datalink)//ncores


    RESULT = pd.DataFrame()

    for i in range(len(WAVELENGTH_LIST)):
        result = analyseLine_singlelambda(datalink, WAVELENGTH_LIST[i], LINE_DICT, setup=setup, k=k,
                                          dispShift=dispShift, order_by_user=order_by_user, nmax=nmax, ncores=ncores,
                                          batch_size=batch_size)
        cols = result.columns.tolist()
        cols = [LINE_NAMES[i] + '_' + col if col != 'source_id' else col for col in cols]
        result.columns = cols
        # print(result.columns)
        if i == 0:
            RESULT = result
        else:
            RESULT = pd.merge(RESULT, result, how='inner', on='source_id')

    return RESULT


def make_output_dataframe(RESULT2, LINE_NAMES):
    """
    Creates an output dataframe by filtering the input dataframe based on line names.

    Args:
        RESULT2 (pandas.DataFrame): The input dataframe containing the spectral data.
        LINE_NAMES (list): A list of line names to filter the dataframe.

    Returns:
        pandas.DataFrame: The filtered output dataframe.

    """
    RESULT = RESULT2.copy()

    for i in range(len(LINE_NAMES)):
        temp_df = RESULT[(RESULT[LINE_NAMES[i] + '_order'] == 0) & \
                    (RESULT[LINE_NAMES[i] + '_ExtremaInRange'] == 1)].copy()

        RESULT = RESULT[~RESULT['source_id'].isin(temp_df['source_id'])].copy()

        temp_df1 = RESULT[(RESULT[LINE_NAMES[i] + '_order'] == 2) & \
                        (RESULT[LINE_NAMES[i] + '_ExtremaInRange'] == 1)].copy()

        RESULT = RESULT[~RESULT['source_id'].isin(temp_df1['source_id'])].copy()

        temp_df2 = RESULT[(RESULT[LINE_NAMES[i] + '_order'] == 'UL')].copy()

        RESULT = RESULT[~RESULT['source_id'].isin(temp_df2['source_id'])].copy()

        TEMP_DF = pd.concat([temp_df, temp_df1, temp_df2], ignore_index=True)

        # print(TEMP_DF['source_id'].nunique())

        RESULT = TEMP_DF.copy()

    relevant_cols = [col for col in TEMP_DF.columns if 'ExtremaInRange' not in col]
    TEMP_DF = TEMP_DF.drop_duplicates(subset=relevant_cols, keep='first')
    return TEMP_DF

def make_spectrum_file(datalink, pwl_bin_step = 0.2):

    pwl_array = np.arange(0, 60 + pwl_bin_step, pwl_bin_step)
    setup = spectrum_tools.XPConstants()

    RP_lambda = spectrum_tools.disp_u_to_lambda(pwl_array, instrument='rp', setup=setup)
    BP_lambda = spectrum_tools.disp_u_to_lambda(pwl_array, instrument='bp', setup=setup)

    #pwl = a*x + b
    a_RP, b_RP = setup.aRP, setup.bRP
    x_RP = (pwl_array - b_RP) / a_RP
    a_BP, b_BP = setup.aBP, setup.bBP
    x_BP = (pwl_array - b_BP) / a_BP

   
