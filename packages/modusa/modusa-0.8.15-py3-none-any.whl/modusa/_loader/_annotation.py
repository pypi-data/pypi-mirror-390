#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 06/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

from pathlib import Path
import warnings

class AnnotationLoader:
    
    def __init__(self):
        pass
        
    @staticmethod
    def _parse_audacity_txt(path, trim):
        
        with open(str(path), "r") as f:
            lines = [line.rstrip("\n") for line in f]
            
        ann = []
        for line in lines:
            start, end, label = line.split("\t")
            start, end = float(start), float(end)
            
            # Incase user has clipped the audio signal, we adjust the annotation
            # to match the clipped audio
            if trim is not None:
                offset = trim[0]
                # Clamp annotation to clip boundaries
                new_start = max(start, trim[0]) - offset
                new_end   = min(end, trim[1]) - offset
                
                # only keep if there's still overlap
                if new_start < new_end:
                    ann.append((new_start, new_end, label))
            else:
                ann.append((start, end, label))
                
        return ann
    
    @staticmethod
    def _parse_ctm(path, trim=None):
        with open(str(path), "r") as f:
            content = f.read().splitlines()
        
        ann = []
        for c in content:
            if not c.strip():
                continue
            
            parts = c.split()
            if len(parts) in (5, 6):
                segment_id, channel, start, dur, label, *rest = parts
                confidence = float(rest[0]) if rest else None
                start, dur = float(start), float(dur)
                end = start + dur
            else:
                warnings.warn(f"'{c}' is not a standard ctm line.")
                continue
    
            # Apply trim if provided
            if trim is not None:
                offset = trim[0]
                new_start = max(start, trim[0]) - offset
                new_end   = min(end, trim[1]) - offset
                if new_start < new_end:
                    ann.append((new_start, new_end, label))
            else:
                ann.append((start, end, label))
        
        return ann

    
    @staticmethod
    def _parse_textgrid(path, trim):
        """
        Parse a Praat TextGrid file into a list of (start, end, label) tuples
        without using any external library.

        Parameters
        ----------
        path : str or Path
            Path to the TextGrid file.
        trim : tuple[float, float] or None
            Optional clip boundaries (start, end) to adjust annotations.

        Returns
        -------
        list[tuple[float, float, str]]
        """
        ann = []
        with open(str(path), "r") as f:
            lines = [line.strip() for line in f]
            
        in_interval = False
        s = e = None
        label = ""
        
        for line in lines:
            # detect start of interval
            if line.startswith("intervals ["):
                in_interval = True
                s = e = None
                label = ""
                continue
            
            if in_interval:
                if line.startswith("xmin ="):
                    s = float(line.split("=")[1].strip())
                elif line.startswith("xmax ="):
                    e = float(line.split("=")[1].strip())
                elif line.startswith("text ="):
                    label = line.split("=", 1)[1].strip().strip('"')
                    
                    # Finished reading an interval
                    if label != "" and s is not None and e is not None:
                        # Apply trim if needed
                        if trim is not None:
                            offset = trim[0]
                            new_start = max(s, trim[0]) - offset
                            new_end   = min(e, trim[1]) - offset
                            if new_start < new_end:
                                ann.append((new_start, new_end, label))
                        else:
                            ann.append((s, e, label))
                    in_interval = False  # ready for next interval
                    
        return ann
    
    
    @staticmethod
    def load(path, trim):
        """
        Load annotation from audatity label
        text file and also ctm file.
    
        Parameters
        ----------
        path: str | PathLike
            label text/ctm file path.
        trim: tuple[number, number] | number | None
            Incase you trimmed the audio signal, this parameter will help clip the annotation making sure that the timings are aligned to the trimmed audio.
            If you trimmed the audio, say from (10, 20), set the trim to (10, 20).
    
        Returns
        -------
        list[tuple, ...]
            - annotation data structure
            - [(start, end, label), ...]
        """
        
        path = Path(path)
        if not path.exists(): raise FileExistsError(f"{path} does not exist")
        
        # Clipping the annotation to match with the clipped audio
        if trim is not None:
            # Map clip input to the right format
            if isinstance(trim, int or float):
                trim = (0, trim)
            elif isinstance(trim, tuple) and len(trim) > 1:
                trim = (trim[0], trim[1])
            else:
                raise ValueError(f"Invalid clip type or length: {type(trim)}, len={len(trim)}")
                
        if path.suffix == ".txt": # Audacity
            ann: list[tuple[float, float, str]] = AnnotationLoader._parse_audacity_txt(path, trim)
        
        elif path.suffix == ".ctm":
            ann: list[tuple[float, float, str]] = AnnotationLoader._parse_ctm(path, trim)
            
        elif path.suffix == ".textgrid":
            ann: list[tuple[float, float, str]] = AnnotationLoader._parse_textgrid(path, trim)
            
        else:
            raise RuntimeError(f"Unsupported file type {path.suffix}")
            
        return ann