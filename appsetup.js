{
    "user_idnt": "ABCD@gmail.com",
    "secrettxt": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "democheck": 0,
    "project": {
        "name": "scase002",
        "winsize": "960,640",
        "preview": 1,
        "fps": "24",
        "detail": "Universe from template",
        "expand": 1,
        "canvas": "500x500"
    },
    "meemerurl": "https://nluserve-ug6ph2hn3q-de.a.run.app",
    "meemerurl_test": "http://localhost:5000/getanim",
    "havegpu": 0,
    "vidtoimg": 1,
    "OSType": "Windows",
    "joint": {
        "makehuman_cmumb": {
            "legs": {
                "include": [
                    "LHipJoint",
                    "RHipJoint"
                ],
                "exclude": []
            },
            "hand": {
                "include": [
                    "LeftShoulder",
                    "RightShoulder"
                ],
                "exclude": []
            },
            "head": {
                "include": [
                    "Neck"
                ],
                "exclude": [
                    "LHipJoint",
                    "RHipJoint"
                ]
            }
        }
    },
    "movies": [
        ".gif",
        ".mp4",
        ".mov",
        ".avi",
        ".wmv",
        ".webm"
    ],
    "images": [
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".tif"
    ],
    "boarditems": [
        {
            "Current rush": [
                {
                    "Play story": [
                        "FPS",
                        "Screen Size (Wide x Height)",
                        "Play from frame#"
                    ]
                },
                {
                    "Replay frames": [
                        "From frame#",
                        "Upto frame#",
                        "FPS"
                    ]
                },
                {
                    "Export video": [
                        "Name of video",
                        "FPS",
                        "Frames range"
                    ]
                },
                {
                    "Delete rush frames": []
                }
            ]
        },
        {
            "Story": [
                {
                    "Save story": [
                        "Name"
                    ]
                },
                {
                    "Open story": [
                        "Name"
                    ]
                },
                {
                    "List stories": [
                        "*NAME LIKE*"
                    ]
                }
            ]
        },
        {
            "Co-ord": [
                {
                    "Save coords": [
                        "Camera Location (3D)",
                        "Camera Looks at/\nWhiteboard Center",
                        "Name"
                    ]
                },
                {
                    "Quick coords": [
                        "Camera Location (3D)",
                        "Camera Looks at/\n(Whiteboard Center)"
                    ]
                },
                {
                    "Open coords": [
                        "Name"
                    ]
                },
                {
                    "List coords": [
                        "*NAME LIKE*"
                    ]
                },
                {
                    "Merge coords": [
                        "X list file",
                        "Y list file",
                        "Z list file"
                    ]
                },
                {
                    "Transform coords": [
                        "Name",
                        "Canvas Size (Wide x Height)",
                        "Screen Size (Wide x Height)"
                    ]
                },
                {
                    "Translate coords": [
                        "Name",
                        "Movement to right",
                        "Movement to bottom"
                    ]
                },
                {
                    "Screen Coordinates": [
                        "Screen Size (Wide x Height)",
                        "Camera Location (3D)",
                        "Camera Looks at/\n(Whiteboard Center)"
                    ]
                }
            ]
        },
        {
            "Audio/ Video": [
                {
                    "List Audios": [
                        "*NAME LIKE*"
                    ]
                },
                {
                    "List Videos": [
                        "*NAME LIKE*"
                    ]
                }
            ]
        },
        {
            "Project": [
                {
                    "Fork project": [
                        "Name"
                    ]
                },
                {
                    "Go Supernova!": []
                }
            ]
        }
    ],
    "procsitems": [
        {
            "fname": "MovieCreate",
            "text": "Add audio upon existing video file",
            "descimage": "imgs/addaudio.png",
            "function": "ui_addaudiotovideo",
            "xtraprocess": {},
            "params": [
                "Video file (with/ without existing audio)",
                "Name of the audio file to be appended",
                "Starting time within video (seconds, default 0)",
                "Starting time for the audio (seconds, default 0)",
                "Length of the audio file to addup (seconds, default 0)",
                "Output file (blank for same video file)"
            ]
        },
        {
            "fname": "MovieCreate",
            "text": "Move my rushes to new or existing set",
            "descimage": "imgs/icon.png",
            "function": "ui_moverushstaging",
            "xtraprocess": {},
            "params": [
                "Output name of the stage",
                "Frame range (1,-1)"
            ]
        },
        {
            "fname": "MediaCreate",
            "text": "Make image/video for a Text or Subtitle",
            "descimage": "imgs/textimg.png",
            "function": "ui_text_image_creation",
            "xtraprocess": {},
            "params": [
                "Output file name",
                "Text to be imaged",
                "Font name (atleast 4 characters)",
                "Font size (default 16)",
                "As characterwise frames (1 char per frame, default NO)?"
            ],
            "additional": "'fill': (1, 1, 1, 255), 'spacing': 4, 'stroke_width': 1"
        },
        {
            "fname": "ModelCreate",
            "text": "Make Panda3d model for frameset/video",
            "descimage": "imgs/createp3dmodel.png",
            "function": "ui_p3dmodel_creation",
            "xtraprocess": {},
            "params": [
                "Input file/folder",
                "Output file name",
                "Frames range (default is all frames: 1,-1)",
                "FPS (leave blank for using video's default)",
                "Final count of frames to be included in model file"
            ]
        },
        {
            "fname": "Pre-process",
            "text": "Basic image manipulation functions",
            "descimage": "imgs/basicmanipul.png",
            "function": "ui_image_manipulation_basic",
            "xtraprocess": {},
            "params": [
                "Input image file",
                "Output file name",
                "Feature of the Image to be changed\n('contrast'/'color'/'brightness'/'sharpness'/'transparent',\n'invert')",
                "New value (number)\n Or type 'range' for values from 0 to 100 (100 images)"
            ]
        },
        {
            "fname": "Pre-process",
            "text": "Advanced image manipulation - Background processing",
            "descimage": "imgs/bgremove.png",
            "function": "ui_image_manipulation_rmback",
            "xtraprocess": {},
            "params": [
                "Input image file",
                "Output file name",
                "Background removal method\n(AI Based) ibrt / static (static color removal)",
                "Color name (white/black/red/green/blue/yellow/panda3d)\nOR Range of color in specified format (see left)"
            ]
        },
        {
            "fname": "Pre-process",
            "text": "Generate illustrations from existing image/s",
            "descimage": "imgs/icon.png",
            "function": "ui_image_manipulation_craft",
            "xtraprocess": {},
            "params": [
                "Input image/s",
                "Output file name",
                "Special effect type (doodle / cartoon / sketch)"
            ]
        },
        {
            "fname": "Pre-process",
            "text": "Make a transparent movie from manipulated rush frames",
            "descimage": "imgs/transmovfromrush.png",
            "function": "image_manual_bgremoval",
            "xtraprocess": {},
            "params": [
                "Final image frame",
                "Output movie name",
                "Color of pen used - default black\n(options: white/black/red/green/blue/yellow/panda3d)"
            ]
        },
        {
            "fname": "Release",
            "text": "Prepare stage for release",
            "descimage": "imgs/stage2release.png",
            "function": "ui_prepare_stage",
            "xtraprocess": {},
            "params": [
                "Stage folder names (comma separated list)",
                "Output Stage Name",
                "Movie format (mp4, mov etc.)"
            ]
        },
        {
            "fname": "Release",
            "text": "Add watermark picture onto given movie",
            "descimage": "imgs/icon.png",
            "function": "ui_prepare_watermark",
            "xtraprocess": {},
            "params": [
                "Watermark image",
                "Input Movie name",
                "Watermark position (in pixels) (default 100,100)",
                "Output file name"
            ]
        }
    ]
}