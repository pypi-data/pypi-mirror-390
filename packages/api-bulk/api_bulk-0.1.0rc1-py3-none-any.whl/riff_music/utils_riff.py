# Next: test_create_midi_lego_riff_combi, Notes, and filename is not correct yet
from typing import List, Union, Dict, Literal
import pandas as pd
from pathlib import Path
from mingus.core import scales, notes, intervals
from mingus.containers import Note
import numpy as np

ScaleType = Union[scales._Scale,Literal["Major","Minor","Natural minor","Ionian","Dorian","Phrygian","Lydian","Mixolydian","Aeolian","Locrian","Harmonic minor","Melodic minor","Whole tone","Chromatic"]]

def create_lego_riff_note_combi(
    # out_prefixname:Union[Path,str]
    lego_block_num: List[int]
    # ,note_lengths: List[int]
    ,directions: Union[List[str],Literal["up","down"]] = ["up","down"]
    # ,bpms: Union[int,List[int]] = 120
    ,n: Union[int,  Dict[Literal["up","down"],int]  ] = 7
    ,key_s: Union[str,List[str]] = ["C", "D", "E", "F", "G", "A", "B", "C#", "Eb", "F#", "Ab", "Bb"]
    ,scale_types: Union[ScaleType, List[ScaleType]] = ["Major","Natural minor","Dorian","Phrygian","Lydian","Mixolydian","Locrian"]
    ,root_degree: Union[Literal["max","min"],int] = "max"
    ,octaves: Union[int,List[int]] = 3
    # ,longer_last_note:Union[bool,int] = 1
    ,include_reversed_notes:bool = True
    ) -> pd.DataFrame:
    # took about 1 hr(including testing)
    import pandas as pd
    # the function runs fine however, the output is still not correctly
    # the notes aren't correct, and somehow not all bmp are exported
    """
    signature function

    build on top of create_lego_riff_note to loop through different parameters and create a combination of midi files
    n can be int or dict  with key "up" and "down" eg n = {"up":6,"down":7}

    output pd.DataFrame {'direction','scale_type','key','octave','notes'}

    """
    # has error with D# as key Gb

    directions_in = list(directions) if isinstance(directions,list) else [directions]
    scale_types_in = list(scale_types) if isinstance(scale_types,list) else [scale_types]
    key_s_in = list(key_s) if isinstance(key_s,list) else [key_s]

    # has error with D# as key Gb, so I want to support D#, Gb as input
    # for other key like Db, G#, A# I would replace them(not to sure that it would throw an error but just replace for safety)
    REPLACE_KEY_DICT = {
        'D#': 'Eb',
        'Gb': 'F#',
        'Db': 'C#',
        'G#': 'Ab',
        'A#': 'Bb'
    }

    if include_reversed_notes:
        reversed_notes_options = [False,True]
    else:
        reversed_notes_options = [False]

    for i, key in enumerate(key_s_in):
        if key in REPLACE_KEY_DICT.keys():
            key_s_in[i] = REPLACE_KEY_DICT[key]


    octaves_in = list(octaves) if isinstance(octaves,list) else [octaves]

    out_df = pd.DataFrame(columns = ["direction","scale_type","key","octave","notes"])
    results = []

    for direction in directions_in:
        for scale_type in scale_types_in:
            for is_reversed_note in reversed_notes_options:
                for key in key_s_in:
                    for octave in octaves_in:
                        if isinstance(n,int):
                            curr_riff_notes = create_lego_riff_note(
                                                lego_block_num = lego_block_num
                                                ,direction = direction
                                                ,n = n
                                                ,key = key
                                                ,scale_type = scale_type
                                                ,root_degree = root_degree
                                                ,octave = octave
                                                ,reverse_notes=is_reversed_note
                                                )
                        elif isinstance(n,dict):
                            curr_riff_notes = create_lego_riff_note(
                                                lego_block_num = lego_block_num
                                                ,direction = direction
                                                ,n = n[direction]
                                                ,key = key
                                                ,scale_type = scale_type
                                                ,root_degree = root_degree
                                                ,octave = octave
                                                ,reverse_notes=is_reversed_note
                                                )
                        curr_dict = {
                            "direction": direction,
                            "scale_type": scale_type,
                            "key": key,
                            "octave": octave,
                            "notes": curr_riff_notes,
                            "reversed_notes": is_reversed_note
                            }
                        results.append(curr_dict)

    out_df = pd.DataFrame(results)
    return out_df
     


def create_midi_lego_riff_combi(
    out_prefixname:Union[Path,str]
    ,lego_block_num: List[int]
    ,note_lengths: List[int]
    ,output_folder: str = ""
    ,directions: Union[List[str],Literal["up","down"]] = ["up","down"]
    ,bpms: Union[int,List[int]] = 120
    ,n: Union[int,  Dict[Literal["up","down"],int]  ] = 7
    ,key_s: Union[str,List[str]] = ["C", "D", "E", "F", "G", "A", "B", "C#", "Eb", "F#", "Ab", "Bb"]
    ,scale_types: Union[ScaleType, List[ScaleType]] = ["Major","Natural minor","Dorian","Phrygian","Lydian","Mixolydian","Locrian"]
    ,root_degree: Union[Literal["max","min"],int] = "max"
    ,octaves: Union[int,List[int]] = 3
    ,longer_last_note:Union[bool,int] = 1
    ,include_reversed_notes:bool = True
    ,use_full_name:bool = False
    ,verbose:int = 1
    ,progress_bar:bool = True
    ) -> None:
    # took about 2 hr(including testing)

    # the function runs fine however, the output is still not correctly
        # the notes aren't correct, and somehow not all bmp are exported
    # has error with D# as key Gb
    
    """
    out_prefixname is without ".mid"
    signature function

    build on top of create_midi_lego_riff_1file to loop through different parameters and create a combination of midi files
    n can be int or dict represents how many cycles you what riff to go through
    
    with key "up" and "down" eg n = {"up":6,"down":7}

    if use_full_name set to True, it will use all combinations of the names,
        if False it would remove the attribute that has only 1 input(eg direction only up, it won't include "_up" in the filename)

    """
    from tqdm import tqdm
    import os_toolkit as ost

    tqdm.pandas()
    # convert single value all into list to support both
    directions_in = list(directions) if isinstance(directions,list) else [directions]
    scale_types_in = list(scale_types) if isinstance(scale_types,list) else [scale_types]
    key_s_in = list(key_s) if isinstance(key_s,list) else [key_s]
    octaves_in = list(octaves) if isinstance(octaves,list) else [octaves]
    bpms_in = list(bpms) if isinstance(bpms,list) else [bpms]
    bpms_str_list = [str(x) + " bmp" for x in bpms_in]

    note_combi_df = create_lego_riff_note_combi(
        lego_block_num = lego_block_num
        ,directions = directions_in
        ,n = n
        ,key_s = key_s_in
        ,scale_types = scale_types_in
        ,root_degree = root_degree
        ,octaves = octaves_in
        ,include_reversed_notes = include_reversed_notes
    )
    # {'direction','scale_type','key','octave','notes'}
    filename_df = note_combi_df.copy()
    filename_df_with_bpm = pd.concat([filename_df] * len(bpms_str_list), ignore_index=True)
    
    bpms_in_repeat = [item for item in bpms_in for _ in range(len(filename_df))]
    bpms_str_repeat = [item for item in bpms_str_list for _ in range(len(filename_df))]

    filename_df_with_bpm['bpm'] = bpms_in_repeat
    filename_df_with_bpm['bpm_str'] = bpms_str_repeat

    if use_full_name is False:
        if len(directions_in) == 1:
            filename_df_with_bpm['direction'] = ""
        if len(scale_types_in) == 1:
            filename_df_with_bpm['scale_type'] = ""

        filename_df_with_bpm['key'] = "Key " + filename_df_with_bpm['key'] 

        if len(octaves_in) == 1:
            filename_df_with_bpm['octave'] = ""
        if len(scale_types_in) == 1:
            filename_df_with_bpm['scale_type'] = ""
        
        if include_reversed_notes:
            filename_df_with_bpm["reversed_notes"] = filename_df_with_bpm["reversed_notes"].astype(str)
            filename_df_with_bpm.loc[filename_df_with_bpm['reversed_notes'] == "True", 'reversed_notes'] = ""
            filename_df_with_bpm.loc[filename_df_with_bpm['reversed_notes'] == "False", 'reversed_notes'] = "reversed"
        else:
            filename_df_with_bpm['reversed_notes'] = ""

        # filename_df_expanded = filename_df.copy()
        
        # created new col: 'bmp'
        # filename_df['bmp'] =
    filename_df_with_bpm['filename'] = filename_df_with_bpm[["direction",'scale_type','key','octave','reversed_notes','bpm_str']].astype(str).agg('_'.join, axis=1)
    filename_df_with_bpm['filename'] = filename_df_with_bpm['filename'].str.replace('_+', '_', regex=True)
    filename_df_with_bpm['filename'] = filename_df_with_bpm['filename'].str.rstrip('_')
    filename_df_with_bpm['filename'] = out_prefixname + "_" + filename_df_with_bpm['filename'] + ".mid"
    filename_df_with_bpm['filepath'] = str(output_folder) + "/" + filename_df_with_bpm['filename'] 

    if verbose >= 1:
        print(f"Total number of midi files generate: {len(filename_df_with_bpm)}")
    if progress_bar:
        filename_df_with_bpm.progress_apply(lambda row: create_midi_repeate_tempo
                                (
                                    out_filename = row["filepath"]
                                    ,note_names = row["notes"]
                                    ,note_lengths = note_lengths
                                    ,bpm = row['bpm']
                                    ,longer_last_note = longer_last_note
                                )
                                
                                , axis = 1)
    else:
        filename_df_with_bpm.apply(lambda row: create_midi_repeate_tempo
                                (
                                    out_filename = row["filepath"]
                                    ,note_names = row["notes"]
                                    ,note_lengths = note_lengths
                                    ,bpm = row['bpm']
                                    ,longer_last_note = longer_last_note
                                )
                                
                                , axis = 1)
    # create_midi_repeate_tempo()
    print() 

    


def create_midi(out_filename: Union[Path, str], 
                note_names: List[str], 
                note_lengths: Union[None, List[float]] = None,
                bpm: float = 120) -> None:
    from music21 import stream, note, midi, tempo
    # high tested
    """
    Create a MIDI file with the specified note names, lengths, and tempo, then save it to the given filename.
    
    Parameters:
    out_filename (Union[Path, str]): The name of the MIDI file to be created.
    note_names (List[str]): List of strings representing the names of the notes to be added to the MIDI file.
    note_lengths (Union[None, List[float]]): List of note durations. 1.0 represents a quarter note. If None, all notes are quarter notes.
    bpm (float): Tempo in beats per minute. Defaults to 120 BPM.
    
    Returns:
    None
    """
    # Create a stream
    s = stream.Stream()

    # Add tempo marking
    t = tempo.MetronomeMark(number=bpm)
    s.append(t)

    # Add notes to the stream
    for i, note_name in enumerate(note_names):
        n = note.Note(note_name)
        if note_lengths is None:
            n.quarterLength = 1  # Each note lasts for one quarter note
        else:
            n.quarterLength = note_lengths[i]
        s.append(n)

    # Create a MIDI file
    mf = midi.translate.streamToMidiFile(s)
    
    # Write the MIDI file
    mf.open(str(out_filename), 'wb')
    mf.write()
    mf.close()

def create_midi_repeate_tempo(
        out_filename:Union[Path,str], 
        note_names:List[str], 
        note_lengths:Union[None,List[float]],
        bpm:float = 120,
        longer_last_note:Union[int,bool] =1,
        ) -> None:
    # high tested
    """
    do similar thing to create_midi but note_lengths is smarter because it would take only the block of note_lengths, and assume to have the same tempo the whole time
    longer_last_note will extend the lastnote for a bit
    """
    from music21 import stream,note,midi,tempo
    s = stream.Stream()

    t = tempo.MetronomeMark(number=bpm)
    s.append(t)
    # if len(note_names) is not divisible by len(note_lengths) it would raise an error
    if len(note_names) % len(note_lengths) != 0:
        raise Exception(f"len(note_names) must be divisible by len(note_lengths), but got len(note_names)={len(note_names)} and len(note_lengths)={len(note_lengths)}")

    n_repeat = len(note_names) // len(note_lengths)
    note_lengths_repeat = note_lengths * n_repeat

    # Add notes to the stream
    for i, note_name in enumerate(note_names):
        n = note.Note(note_name)
        if note_lengths is None:
            n.quarterLength = 1  # Each note lasts for one quarter note
        else:
            if (i == len(note_names) - 1):
                n.quarterLength = note_lengths_repeat[i] + longer_last_note
            else:
                n.quarterLength = note_lengths_repeat[i]
        s.append(n)

    # Create a MIDI file
    mf = midi.translate.streamToMidiFile(s)
    
    # Write the MIDI file
    mf.open(out_filename, 'wb')
    mf.write()
    mf.close()

    pass

    # print(f"MIDI file '{filename}' has been created with notes {', '.join(note_names)}.")


def _get_scale(key: str, scale_type: ScaleType) -> scales._Scale:
        # Helper function to get the appropriate scale object
        scale_dict = {
            "major": scales.Major,
            "minor": scales.NaturalMinor,
            "natural minor": scales.NaturalMinor,
            "ionian": scales.Ionian,
            "dorian": scales.Dorian,
            "phrygian": scales.Phrygian,
            "lydian": scales.Lydian,
            "mixolydian": scales.Mixolydian,
            "aeolian": scales.Aeolian,
            "locrian": scales.Locrian,
            # Add more scales as needed
            "harmonic minor": scales.HarmonicMinor,
            "melodic minor": scales.MelodicMinor,
            "whole tone": scales.WholeTone,
            "chromatic": scales.Chromatic,
            # "major pentatonic": scales.,

        }
        # no pentatonic scale in based on migus 0.6.1
        
        if isinstance(scale_type, scales._Scale):
            return scale_type
        elif isinstance(scale_type, type) and issubclass(scale_type, scales._Scale):
            return scale_type(key)
        elif isinstance(scale_type, str):
            scale_type = scale_type.lower()
            if scale_type in scale_dict.keys():
                return scale_dict[scale_type](key)
            else:
                raise ValueError(f"Unsupported scale type string: {scale_type}")
        else:
            raise TypeError(f"Unsupported scale type: {type(scale_type)}")

def convert_num_to_scale(scale_degrees:List[int], 
                         key: str = "C", 
                         octave: int = 4,
                         scale_type: ScaleType = scales.Major,
                         out_as_str:bool = True
                         ) -> Union[List[str], List[Note]]:
    scales_obj = _get_scale(key, scale_type)
    scales = scales_obj.ascending()
    # shift index by 1
    #  0 & 1 would be the same note
    # -1 -2 will refer to the note below
    scales = [scales[0]] + scales
    scales_notes = []

    for degree in scale_degrees:
        curr_octave = degree // 7
        if degree % 7 == 0:
            curr_degree = 7
            add_to_octave = 0
        else:
            curr_degree = degree % 7
            add_to_octave = degree // 7
            if add_to_octave < 0:
                curr_degree += 1

        curr_note = Note(scales[curr_degree],octave+add_to_octave )
        scales_notes.append(curr_note)

    scales_notes_str = [f"{note.name}{note.octave}" for note in scales_notes]

    if out_as_str:
        return scales_notes_str
    else:
        return scales_notes

def convert_num_to_scale(
    scale_degrees: List[int],
    key: str = "C",
    octave: int = 4,
    scale_type: ScaleType = scales.Major,
    out_as_str: bool = True
    ) -> Union[List[str], List[Note]]:

    # provided by o1, as of Oct 23, 2024

    # Initialize the scale
    scales_obj = _get_scale(key, scale_type)
    scales_notes = scales_obj.ascending()

    # shift index by 1
    #  0 & 1 would be the same note
    # -1 -2 will refer to the note below

    scale_degrees_mutate = []
    for degree in scale_degrees:
        if degree > 0:
            degree_mutate = degree
        else:
            degree_mutate = degree + 1
        scale_degrees_mutate.append(degree_mutate)
    
    # Map note names to semitone numbers
    note_semitone_mapping = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3,
                             'E': 4, 'F': 5, 'F#': 6, 'G': 7,
                             'G#': 8, 'A': 9, 'A#': 10, 'B': 11,

                             'Db': 1, 'Eb':3,'Gb':6, 'Ab':8, 'Bb': 10,
                             'E#': 5, 'B#': 0,
                             }
    semitone_number_to_note_name = {v: k for k, v in note_semitone_mapping.items()}
    
    # Get the key's semitone number
    key_semitone_number = note_semitone_mapping[key]
    
    # Calculate semitone offsets for the scale
    semitone_offsets = []
    for note_name in scales_notes:
        note_semitone_number = note_semitone_mapping[note_name]
        semitone_offset = (note_semitone_number - key_semitone_number) % 12
        semitone_offsets.append(semitone_offset)
    
    # Starting MIDI note number
    starting_midi_number = 12 * (octave + 1) + key_semitone_number
    
    # Convert scale degrees to notes
    scales_output = []
    len_scale = len(semitone_offsets)
    for i, degree in enumerate(scale_degrees_mutate):
        if degree >= 8:
            # for debugging
            print()
        octave_adjustment = (degree - 1) // (len_scale-1)
        degree_index = (degree - 1) % (len_scale-1)
        semitone_offset = semitone_offsets[degree_index] + octave_adjustment * 12
        total_semitone_number = starting_midi_number + semitone_offset
        note_semitone_number = total_semitone_number % 12
        note_octave = (total_semitone_number // 12) - 1
        note_name = semitone_number_to_note_name[note_semitone_number]
        curr_note = Note(note_name, note_octave)
        scales_output.append(curr_note)

    scales_notes_str = [f"{note.name}{note.octave}" for note in scales_output]
    if out_as_str:
        return scales_notes_str
    else:
        return scales_output


def make_num_seq(num_block:List[int],n:int = 7, increment:int = 1,as_np:bool=False) -> Union[List[int], np.ndarray[np.int_]]:


    """
    Generates a sequence of numbers by repeating the given `num_block` list `n` times and incrementing each element by `increment`.
    
    Args:
        num_block (List[int]): The initial list of numbers.
        n (int, optional): The number of times to repeat the `num_block` list. Defaults to 7.
        increment (int, optional): The amount to increment each element by. Defaults to 1.
        as_np (bool, optional): Whether to return the result as a NumPy array. Defaults to False.
    
    Returns:
        List[int] or np.ndarray: The generated sequence of numbers. If `as_np` is True, returns a NumPy array.
    """
    import numpy as np

    base_np_array = np.array(num_block)
    out_array = np.array(num_block)
    for i in range(1,n+1):
        np_array = base_np_array + i*increment
        out_array = np.append(out_array, np_array)
    out_list = out_array.tolist()

    if as_np:
        return out_array
    else:
        return out_list

def make_num_degree_down(
        num_block:List[int],
        n:int = 7, 
        increment:int = -1,
        as_np:bool=False,
        as_positive:bool = True,
        root_degree:Union[Literal["max","min"],int] = "max"
        )-> Union[List[int], np.ndarray[np.int_]]:
    """ 
    the reason I have to write this function because 0,1 will be interpreted as the root note and only -1 means the 1 step below root note
    it's only for my lib and it won't be useful somewhere else

    as_positive will +8 to make the num_degree become positive

    """
    if root_degree in ["max"]:
        root_num = max(num_block)
    elif root_degree in ["min"]:
        root_num = min(num_block)
    elif isinstance(root_degree, int):
        root_num = root_degree

    num_block_negative = [num-root_num for num in num_block]

    base_np_array = np.array(num_block_negative)
    out_array_negative = np.array(num_block_negative)
    for i in range(1,n+1):
        np_array = base_np_array + i*increment
        out_array_negative = np.append(out_array_negative, np_array)
    
    out_array_positive = out_array_negative + 8
    out_list_negative = out_array_negative.tolist()
    out_list_positive = out_array_positive.tolist()

    if as_np:
        if as_positive:
            return out_array_positive
        else:
            return out_array_negative
    else:
        if as_positive:
            return out_list_positive
        else:
            return out_list_negative

def create_lego_riff_note(
        lego_block_num: List[int]
        ,direction: Literal["up","down"]
        ,n: int = 7
        ,key:str = "C"
        ,scale_type:ScaleType = "Major"
        ,root_degree:Union[Literal["max","min"],int] = "max"
        ,octave:int = 3
        ,out_as_str:bool = True
        ,reverse_notes:bool = False
        ) -> Union[List[Note],List[str]]:
    # medium tested
    """
    Generate a musical riff based on a sequence of Lego block numbers.

    Args:
        lego_block_num (List[int]): A list of Lego block numbers.
        direction (Literal["up","down"]): The direction of the riff. "up" for ascending and "down" for descending.
        n (int, optional): The number of notes in the riff. Defaults to 7.
        key (str, optional): The key of the riff. Defaults to "C".
        scale_type (ScaleType, optional): The type of scale to use. Defaults to "Major".
        root_degree (Union[Literal["max","min"],int], optional): The root degree of the scale. Defaults to "max".
        out_as_str (bool, optional): Whether to output the riff as a list of strings or a list of Note objects. Defaults to True.

        reverse_notes will reverse the order of the notes(lego_block_num)

    Returns:
        Union[List[Note],List[str]]: The generated riff as a list of Note objects or a list of strings.

    Raises:
        ValueError: If the direction is neither "up" nor "down".
    """
    
    lego_block_num_reversed = lego_block_num[::-1]
    if reverse_notes:
        if direction.lower() in ["up"]:
            scale_degrees = make_num_seq(lego_block_num_reversed, n=n, increment=1)
        elif direction.lower() in ["down"]:
            scale_degrees = make_num_degree_down(lego_block_num_reversed, n=n, increment=-1,root_degree=root_degree)
        else:
            raise ValueError("direction must be either 'up' or 'down'")
    else:
        if direction.lower() in ["up"]:
            scale_degrees = make_num_seq(lego_block_num, n=n, increment=1)
        elif direction.lower() in ["down"]:
            scale_degrees = make_num_degree_down(lego_block_num, n=n, increment=-1,root_degree=root_degree)
        else:
            raise ValueError("direction must be either 'up' or 'down'")
    
    riff_notes_obj = convert_num_to_scale(scale_degrees,scale_type=scale_type,key=key,out_as_str=False,octave=octave)
    riff_notes_str = convert_num_to_scale(scale_degrees,scale_type=scale_type,key=key,out_as_str=True,octave=octave)

    if out_as_str:
        return riff_notes_str
    else:
        return riff_notes_obj

def create_midi_lego_riff_1file(
    out_filename:Union[Path,str]
    ,lego_block_num: List[int]
    ,note_lengths: List[int]
    ,direction: Literal["up","down"]
    ,bpm:int = 120
    ,n: int = 7
    ,key:str = "C"
    ,scale_type:ScaleType = "Major"
    ,root_degree:Union[Literal["max","min"],int] = "max"
    ,longer_last_note:Union[bool,int] = 1
    ) -> None:

    """
    signature function
    """

    # medium tested
    riff_notes = create_lego_riff_note(
        lego_block_num = lego_block_num
        ,direction = direction
        ,n = n
        ,key = key
        ,scale_type = scale_type
        ,root_degree = root_degree
        ,out_as_str = True
        )
    
    create_midi_repeate_tempo(out_filename,riff_notes,note_lengths,bpm=bpm,longer_last_note=longer_last_note)

def permutation_non_repeated(sequence: List[int],exclude_ori_sequence:bool = False) -> List[List[int]]:
    """
    create a permutation of the sequence that does not contain repeated elements(next element)
    """
    from collections import Counter
    def backtrack(current: List[int], remaining: Counter):
        if len(current) == len(sequence):
            arrangements.append(current[:])
            return

        for num in remaining:
            if remaining[num] > 0 and (not current or num != current[-1]):
                current.append(num)
                remaining[num] -= 1
                backtrack(current, remaining)
                current.pop()
                remaining[num] += 1

    arrangements = []
    backtrack([], Counter(sequence))
    if exclude_ori_sequence:
        arrangements.remove(sequence)
    return arrangements

