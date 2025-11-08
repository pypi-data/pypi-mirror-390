import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

import time
from . import line_analysis as la
from . import spectrum_tools as st
from . import dataIO as dio
import numpy as np
import pickle
from .config import _CONFIG
import os

def run_pipeline(sources_table,
                source_id_column='source_id',
                xp_continuous_output_file='xp_continuous_downloaded.csv',
                eq_widths_output_file='Test_EqWidths',
                extrema_output_file='Test_Extrema',
                time_stamps=False,
                produce_eq_widths=True):
    """
    Run the XPy-TEAL analysis pipeline for a set of sources.
    This function orchestrates the end-to-end processing of XP spectra: it reads user
    configuration, downloads or loads continuous XP spectra for the provided sources,
    detects spectral features (extrema) in derivative space, optionally computes
    equivalent widths for a set of spectral lines, and writes selected outputs to
    disk.
    Parameters
    ----------
    sources_table : str or pandas.DataFrame or path-like
        Identifier for the input source list. This is forwarded to the
        st.download_xp_spectra_if_needed(...) helper which will either download,
        read or otherwise prepare the continuous XP spectra database for the
        listed sources. The exact accepted types/semantics depend on that helper.
    source_id_column : str, optional
        Name of the column in sources_table that uniquely identifies each source.
        Default: 'source_id'.
    xp_continuous_output_file : str, optional
        Base filename (without directory) used by st.download_xp_spectra_if_needed
        when saving or reading the continuous XP spectra. Default: 'xp_continuous_downloaded.csv'.
    eq_widths_output_file : str, optional
        Base filename (without directory/extension) used when saving equivalent-width
        outputs. Default: 'Test_EqWidths'.
    extrema_output_file : str, optional
        Base filename (without directory/extension) used when saving extrema
        information as a pickle. Default: 'Test_Extrema'.
    time_stamps : bool, optional
        When True, print elapsed timing information for major pipeline stages.
        Default: False.
    produce_eq_widths : bool, optional
        When True, perform equivalent-width calculations after extrema detection.
        When False, equivalent-width steps are skipped and the function returns None.
        Default: True.
    Behavior / Side effects
    -----------------------
    - Reads runtime/user configuration via dio.read_xml() to obtain:
        - output_format (e.g., 'csv')
        - provide_all_extrema (bool)
        - provide_equivalent_widths (bool)
        - number_of_cores (int)
        - list_of_default_lines, list_of_line_wavelengths (line selection)
    - Downloads or loads XP spectra for the provided sources via
        st.download_xp_spectra_if_needed(...). This may read or write the file named
        by xp_continuous_output_file.
    - Builds a list of line wavelengths/names by combining default and user-requested lines.
    - Detects lines/extrema in derivative space in parallel using
        la.getLinesInDeriv_parallel(...). The number of parallel workers is taken
        from the user configuration.
    - If provide_all_extrema (from user XML) is True, saves the complete extrema
        information (LINE_DICT) to a pickle file under _CONFIG["DATA_DIR"] using the
        given extrema_output_file base name ('.pkl' extension).
    - If produce_eq_widths is True, computes equivalent widths across the chosen
        wavelengths using la.analyseLine_all_wavelengths(...), converts results to a
        pandas DataFrame via la.make_output_dataframe(...) and, if configured
        (provide_equivalent_widths flag in user XML), writes the results to disk in
        the requested output_format (currently 'csv' is supported in the pipeline).
    - Deletes intermediate LINE_DICT to free memory before returning.
    Return value
    ------------
    pandas.DataFrame or None
        If equivalent-width computation was performed and requested for output,
        returns a pandas DataFrame (RESULT) containing the computed equivalent
        widths and related columns. If equivalent-width computation was skipped
        (produce_eq_widths=False) the function returns None.
    Files written
    -------------
    - When provide_all_extrema is True: DATA_DIR/<extrema_output_file>.pkl (pickle of LINE_DICT)
    - When provide_equivalent_widths is True and output_format == 'csv':
        DATA_DIR/<eq_widths_output_file>.csv
    Note: DATA_DIR is taken from the global _CONFIG["DATA_DIR"] used by the package.
    Notes and assumptions
    ---------------------
    - The function relies on several module-level helpers and globals (dio, st, la,
        _CONFIG) and therefore will raise whatever exceptions those helpers raise
        (network/IO errors, parsing errors, pandas/numPy exceptions, pickle errors, etc.).
    - The deconvolution order K is fixed to 2 within the pipeline.
    - Parallel processing is delegated to la.getLinesInDeriv_parallel and
        la.analyseLine_all_wavelengths and controlled by the number_of_cores value in
        the user XML.
    - The function prints progress messages; use time_stamps=True for additional timing diagnostics.
    Example
    -------
    # Basic usage (assuming package imports and a valid sources_table):
    result_df = run_pipeline(sources_table,
                            xp_continuous_output_file='xp_cont.csv',
                            eq_widths_output_file='eqw_results',
                            extrema_output_file='all_extrema',
                            time_stamps=True,
                            produce_eq_widths=True)
    Raises
    ------
    Any exception raised by underlying helpers (dio.read_xml, st.download_xp_spectra_if_needed,
    la.* functions, file I/O, pickle) will propagate to the caller.
    """

    if time_stamps:
        print("Starting XPy-TEAL pipeline...")
        print("------------------------------------")
        print("------------------------------------")
        t1 = time.time()

    user_input = dio.read_xml()

    t = st.download_xp_spectra_if_needed(sources_table,
                                        source_id_column=source_id_column,
                                        output_file=xp_continuous_output_file)
    
    print('Number of sources to analyse: ', len(t))

    output_format = user_input['output_format']
    provide_all_extrema_flag = user_input['provide_all_extrema']
    provide_eq_widths_flag = user_input['provide_equivalent_widths']


    # general parameters:
    K = 2 # the order for local de-convolution
    n_cores = int(user_input['number_of_cores'])

    default_line_wavelengths = la.get_default_line_wavelengths(user_input['list_of_default_lines'])
    requested_lines = la.get_list_of_wavelegths(user_input['list_of_line_wavelengths'])

    wavelength_list = default_line_wavelengths + requested_lines
    wavelength_list = np.array(wavelength_list)

    LINE_NAMES = la.getLineNames(user_input['list_of_default_lines'], 
                                    user_input['list_of_line_wavelengths'])
    print('Total number of lines to analyse: ', len(LINE_NAMES))

    if time_stamps:
        t2 = time.time()
        print("Time to read/download data and set up parameters: ", t2-t1)

    LINE_DICT = la.getLinesInDeriv_parallel(datalink=t,
                                            n_cores=n_cores)
    
    if time_stamps:
        t3 = time.time()
        print("Time to get lines in derivative: ", t3-t2)

    if provide_all_extrema_flag:
        extrema_path = os.path.join(_CONFIG["DATA_DIR"], extrema_output_file + '.pkl')
        print("Saving all extrema information to file " + extrema_path)
        with open(extrema_path, 'wb') as f:
            pickle.dump(LINE_DICT, f)

    if produce_eq_widths:

        RESULT = la.analyseLine_all_wavelengths(datalink=t,WAVELENGTH_LIST=wavelength_list,
                                                LINE_NAMES=LINE_NAMES, LINE_DICT=LINE_DICT,
                                                k = K, ncores=n_cores)
        
        RESULT = la.make_output_dataframe(RESULT, LINE_NAMES)

        if time_stamps:
            t4 = time.time()
            print("Time to get equivalent widths: ", t4-t3)

        if provide_eq_widths_flag:
            out_path = os.path.join(_CONFIG["DATA_DIR"], eq_widths_output_file + "." + output_format)
            print("Saving equivalent widths to file " + out_path)
            print("------------------------------------")
            print("------------------------------------")
            if output_format == 'csv':
                RESULT.to_csv(os.path.join(_CONFIG["DATA_DIR"], eq_widths_output_file + '.csv'), index=False)

            # it will be the fastest to write to parquet
            # elif output_format == 'parquet':
            #     RESULT.to_parquet(os.path.join(DATA_DIR, eq_widths_output_file + '.parquet'), index=False)


    else:
        print("Skipping equivalent width calculations as per user request.")
        print("------------------------------------")
        print("------------------------------------")
        RESULT = None

    del LINE_DICT

    print("Pipeline completed.")
    return RESULT