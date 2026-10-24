"""Upload, remove burned-in text, poll and download an authorized video."""
import argparse
import json
from pathlib import Path
from client import add_arguments, run


def make_body(args):
    rect = json.loads(Path(args.rect_json).read_text()) if args.rect_json else None
    if args.mode == 'all_area' and rect is not None:
        raise ValueError('all_area must omit --rect-json')
    rects = [rect] if args.mode == 'sel_area' else rect
    if args.mode != 'all_area':
        if not isinstance(rects, list) or not rects:
            raise ValueError('sel_area needs one rectangle object; multi_area needs a non-empty array')
        for box in rects:
            if not isinstance(box, dict) or set(box) != {'x1', 'y1', 'x2', 'y2'}:
                raise ValueError('Each rectangle needs x1, y1, x2, y2 in source pixels')
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in box.values()):
                raise ValueError('Coordinates must be numeric')
            if not (0 <= box['x1'] < box['x2'] and 0 <= box['y1'] < box['y2']):
                raise ValueError('Invalid rectangle bounds')
    return {'type': 'remove_text', 'mode': args.mode, 'rect': rect}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    parser.add_argument('--mode', choices=['all_area', 'sel_area', 'multi_area'], default='all_area')
    parser.add_argument('--rect-json', help='JSON object for sel_area, array for multi_area')
    run(parser, make_body)
