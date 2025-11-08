import os
import re
import numpy as np
import obspy

#######################################
# Obspy functions
#######################################
def read_seismic_file(seismic_file, separate_sources=False):
    '''
    Read a seismic file and return a list of streams, one for each source.

    Parameters
    ----------
    seismic_file : str
        The path to the seismic file.
    separate_sources : bool, optional
        If True, separate the traces into different streams based on the original_field_record_number.
        Default is False.
        
    Returns
    -------
    stream : obspy.Stream
        The stream object containing the seismic data.
    '''
    # Read the seismic file
    stream = obspy.read(seismic_file,unpack_trace_headers=True)

    input_format = check_format(stream)

    if input_format == 'seg2':
        # Preserve original SEG2 coordinate information before conversion
        original_seg2_coords = []
        for trace_index, trace in enumerate(stream):
            coord_info = {
                'receiver_x': 0.0,
                'receiver_y': 0.0,
                'receiver_z': 0.0,
                'source_x': 0.0,
                'source_y': 0.0,
                'source_z': 0.0,
                'trace_index': trace_index
            }
            
            # Extract coordinates from SEG2 headers with multiple field name variations
            if hasattr(trace.stats, 'seg2'):
                seg2 = trace.stats.seg2
                
                # Try different field names for receiver location
                receiver_location_fields = ['RECEIVER_LOCATION', 'RECEIVER_LOCATION_X', 'RECEIVER_X', 'REC_X']
                for field in receiver_location_fields:
                    if hasattr(seg2, field):
                        try:
                            coord_info['receiver_x'] = float(getattr(seg2, field))
                            break
                        except (ValueError, TypeError):
                            continue
                
                # Try different field names for source location  
                source_location_fields = ['SOURCE_LOCATION', 'SOURCE_LOCATION_X', 'SOURCE_X', 'SRC_X']
                for field in source_location_fields:
                    if hasattr(seg2, field):
                        try:
                            coord_info['source_x'] = float(getattr(seg2, field))
                            break
                        except (ValueError, TypeError):
                            continue
                
                # Look for elevation/Z coordinates
                receiver_z_fields = ['RECEIVER_ELEVATION', 'RECEIVER_Z', 'REC_Z', 'RECEIVER_LOCATION_Z']
                for field in receiver_z_fields:
                    if hasattr(seg2, field):
                        try:
                            coord_info['receiver_z'] = float(getattr(seg2, field))
                            break
                        except (ValueError, TypeError):
                            continue
                            
                source_z_fields = ['SOURCE_ELEVATION', 'SOURCE_Z', 'SRC_Z', 'SOURCE_LOCATION_Z']  
                for field in source_z_fields:
                    if hasattr(seg2, field):
                        try:
                            coord_info['source_z'] = float(getattr(seg2, field))
                            break
                        except (ValueError, TypeError):
                            continue
            
            # If no coordinates found in headers, assign based on trace index (common fallback)
            if coord_info['receiver_x'] == 0.0 and coord_info['source_x'] == 0.0:
                # Assign receiver positions based on trace index (1-meter spacing as default)
                coord_info['receiver_x'] = float(trace_index + 1)
                # Assign source position (common to assume source at trace 1 position)
                coord_info['source_x'] = 1.0
            
            original_seg2_coords.append(coord_info)
        
        input_format = 'segy'
        # Extract the FFID from the file name (any number in the file name)
        file_base_name = os.path.basename(seismic_file) # Get the base name of the file
        file_base_name, _ = os.path.splitext(file_base_name) # Remove the extension
        ffid = re.findall(r'\d+', file_base_name) # Find any number in the file name
        if ffid:
            ffid = int(ffid[0])
        else:
            ffid = 1

        stream.write('tmp.sgy',format='SEGY',data_encoding=5, byteorder='>')
        stream = obspy.read('tmp.sgy',unpack_trace_headers=True)
        os.remove('tmp.sgy')
        
        # Calculate coordinate scalar for preserved coordinates
        all_coords = []
        for coord_info in original_seg2_coords:
            all_coords.extend([coord_info['receiver_x'], coord_info['receiver_y'], coord_info['receiver_z'],
                             coord_info['source_x'], coord_info['source_y'], coord_info['source_z']])
        
        # Remove zeros and calculate max decimals
        non_zero_coords = [coord for coord in all_coords if coord != 0.0]
        if non_zero_coords:
            max_decimals = get_max_decimals(np.array(non_zero_coords))
            coordinate_scalar = 10 ** max_decimals
        else:
            coordinate_scalar = 1  # Default scalar when no coordinates available
        
        for trace_index, trace in enumerate(stream):
            trace.stats[input_format].trace_header.trace_sequence_number_within_line = trace_index+1 #tracl
            trace.stats[input_format].trace_header.trace_sequence_number_within_segy_file = trace_index+1 #tracr
            trace.stats[input_format].trace_header.original_field_record_number = ffid #fldr
            trace.stats[input_format].trace_header.trace_number_within_the_original_field_record = trace_index+1 #tracf
            
            # Apply preserved coordinates with proper scalar
            if trace_index < len(original_seg2_coords):
                coord_info = original_seg2_coords[trace_index]
                trace.stats[input_format].trace_header.scalar_to_be_applied_to_all_coordinates = int(-coordinate_scalar)
                trace.stats[input_format].trace_header.group_coordinate_x = int(coord_info['receiver_x'] * coordinate_scalar)
                trace.stats[input_format].trace_header.group_coordinate_y = int(coord_info['receiver_y'] * coordinate_scalar)
                trace.stats[input_format].trace_header.receiver_group_elevation = int(coord_info['receiver_z'] * coordinate_scalar)
                trace.stats[input_format].trace_header.source_coordinate_x = int(coord_info['source_x'] * coordinate_scalar)
                trace.stats[input_format].trace_header.source_coordinate_y = int(coord_info['source_y'] * coordinate_scalar)
                trace.stats[input_format].trace_header.surface_elevation_at_source = int(coord_info['source_z'] * coordinate_scalar)
    
    if separate_sources:
        stream = separate_streams(stream)

    return stream

def check_format(stream):
    '''
    Check the input format of the stream.
    
    Parameters
    ----------
    stream : obspy.Stream
        The stream object containing the seismic data.
        
    Returns
    -------
    input_format : str
        The input format of the stream.
    '''

    if hasattr(stream[0].stats, 'su'):
        input_format = 'su'
    elif hasattr(stream[0].stats, 'segy'):
        input_format = 'segy'
    elif hasattr(stream[0].stats, 'seg2'):
        input_format = 'seg2'
    else:
        raise ValueError('The input format is not recognized')
    
    return input_format

def separate_streams(stream):
    '''
    Separate the traces into different streams based on the original_field_record_number.

    Parameters
    ----------
    stream : obspy.Stream
        The stream object containing the seismic data.

    Returns
    -------
    streams : list
        A list of streams, one for each source.
    '''
    
    # Check the input format
    input_format = check_format(stream)
        
    # Get the unique original_field_record_number values
    unique_record_numbers = sorted(list(set(trace.stats[input_format].trace_header.original_field_record_number for trace in stream)))
    
    # Initialize an empty list to store the shot gathers in different streams
    streams = []
    
    # Iterate over the unique record numbers
    for record_number in unique_record_numbers:
        # Select the traces with the current record number and add them to the list
        substream = obspy.Stream([trace for trace in stream if trace.stats[input_format].trace_header.original_field_record_number == record_number])
        streams.append(substream)
    
    return streams

def merge_streams(streams):
    """
    Merge multiple streams into a single stream.

    Parameters
    ----------
    streams : list
        A list of obspy.Stream objects to be merged.

    Returns
    -------
    merged_stream : obspy.Stream
        The merged stream containing all traces from the input streams.
    """
    
    merged_stream = streams[0].copy()  # Start with a copy of the first stream
    for stream in streams[1:]:  # Iterate over the rest of the streams
        merged_stream += stream  # Add each stream to the merged stream

    return merged_stream

def swap_traces(stream, trace1, trace2):
    """
    Switch the amplitude data of two traces in a stream.
    
    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    trace1 : int
        Index of the first trace.
    trace2 : int
        Index of the second trace.
        
    Returns
    -------
    stream : obspy.Stream
        Stream with the amplitude data of the two traces switched.
    """

    input_format = check_format(stream)

    # Copy the traces based on the trace indices in header
    tr1 = [trace for trace in stream if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == trace1]
    tr2 = [trace for trace in stream if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == trace2]

    if not tr1 or not tr2:
        raise ValueError("Trace not found in the stream")

    tr1 = tr1[0]
    tr2 = tr2[0]
    
    # Switch the amplitude data
    tr1.data, tr2.data = tr2.data.copy(), tr1.data.copy()

    return stream

def remove_trace(stream, removed_trace):
    """
    Remove trace from a stream based on their trace numbers.

    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    removed_trace : int
        First trace number to remove.

    Returns
    -------
    stream : obspy.Stream
        Stream with the specified traces removed.
    """

    input_format = check_format(stream)

    # Remove trace based on the trace numbers in header
    for trace in stream :
        if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == removed_trace:
            stream.remove(trace)
            break

    return stream

def move_trace(stream, moved_trace, new_position):
    """
    Move trace in a stream based on their trace numbers.

    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    moved_trace : int
        First trace number to move.
    new_position : int
        New position for the trace.

    Returns
    -------
    stream : obspy.Stream
        Stream with the specified trace moved to the new position.
    """

    input_format = check_format(stream)

    # Find the trace to move
    for i, trace in enumerate(stream):
        if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == moved_trace:
            # Remove the trace from its current position
            stream.remove(trace)
            # Insert it at the new position
            stream.insert(new_position, trace)
            break

    # Reset the trace sequence numbers
    for i, trace in enumerate(stream):
        trace.stats[input_format].trace_header.trace_sequence_number_within_line = i + 1
        trace.stats[input_format].trace_header.trace_sequence_number_within_segy_file = i + 1
        trace.stats[input_format].trace_header.original_field_record_number = trace.stats[input_format].trace_header.original_field_record_number
        trace.stats[input_format].trace_header.trace_number_within_the_original_field_record = i + 1

    return stream

def mute_trace(stream, muted_trace):
    """
    Mute trace in a stream based on their trace numbers.

    Parameters
    ----------
    stream : obspy.Stream
        Stream containing the traces.
    muted_trace : int
        First trace number to mute.

    Returns
    -------
    stream : obspy.Stream
        Stream with the specified traces muted.
    """

    input_format = check_format(stream)

    # Mute trace based on the trace numbers in header
    for trace in stream :
        if trace.stats[input_format].trace_header.trace_number_within_the_original_field_record == muted_trace:
            trace.data = np.zeros(trace.data.shape)
            break

    return stream

def swap_header_format(stream,output_format):

    output_format = output_format.lower()

    input_format = check_format(stream)
    
    for trace in stream:
        # Get the AttribDict for the input format
        attrib_dict = trace.stats[input_format]
        # Create a new AttribDict for the output format
        trace.stats[output_format] = obspy.core.AttribDict()

        # Iterate over the items in the AttribDict
        for key, value in attrib_dict.items():
            trace.stats[output_format][key] = value

        trace.stats._format = output_format.upper()

        # Delete the input format AttribDict
        if input_format != output_format:
            del trace.stats[input_format]

    stream._format = output_format.upper()

    return stream

def get_max_decimals(positions):
    """
    Calculate the maximum number of decimal places in coordinate positions.
    Handles edge cases like empty arrays and invalid values.
    """
    # Handle empty or invalid input
    if len(positions) == 0:
        return 0
    
    # Extract unique x and z positions, filtering out NaN and inf values
    unique_positions = np.unique(positions)
    valid_positions = unique_positions[np.isfinite(unique_positions)]
    
    if len(valid_positions) == 0:
        return 0

    # Function to count decimals
    def count_decimals(number):
        try:
            s = str(float(number))
            if '.' in s:
                decimal_part = s.split('.')[1]
                # Remove trailing zeros
                decimal_part = decimal_part.rstrip('0')
                return len(decimal_part)
            else:
                return 0
        except (ValueError, TypeError):
            return 0

    # Count decimals for each unique position
    decimals = [count_decimals(pos) for pos in valid_positions]

    # Return the maximum number of decimals, with a reasonable upper limit
    return min(max(decimals) if decimals else 0, 6)  # Cap at 6 decimal places


def assisted_picking(trace_data, time_array, y_pick, smoothing_window_size, deviation_threshold, picking_window_size):
    """
    Adjust pick position using assisted picking algorithm.

    Parameters:
        trace_data (np.ndarray): The trace data array.
        time_array (np.ndarray): The time array corresponding to the trace data.
        y_pick (float): The initial pick time.
        smoothing_window_size (int): Window size for smoothing.
        deviation_threshold (float): Threshold multiplier for deviation.
        picking_window_size (int): Window size for deviation search.

    Returns:
        float: Adjusted pick time.
    """
    trace_data = np.array(trace_data, dtype=float)
    if np.max(np.abs(trace_data)) != 0:
        trace_data = trace_data / np.max(np.abs(trace_data))
    smoothed_trace_data = np.convolve(trace_data, np.ones(smoothing_window_size)/smoothing_window_size, mode='same')

    pick_index = np.argmin(np.abs(time_array - y_pick))
    window_start = 0
    window_end = pick_index
    mean_window = np.mean(np.abs(smoothed_trace_data[window_start:window_end]))
    std_window = np.std(np.abs(smoothed_trace_data[window_start:window_end]))
    threshold = std_window * deviation_threshold

    for j in range(pick_index, min(pick_index + picking_window_size, len(smoothed_trace_data))):
        if np.abs(smoothed_trace_data[j] - mean_window) > threshold:
            return time_array[j]
    return y_pick