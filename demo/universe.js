{
    "actions": [
        {
            "func": "move",
            "syns": [
                "moving",
                "move",
                "moves",
                "moved"
            ],
            "jjrb": [],
            "show": 0
        },
        {
            "func": "locate",
            "syns": [
                "looks",
                "locate",
                "looked",
                "locating",
                "looking",
                "locates",
                "located",
                "look"
            ],
            "jjrb": [],
            "show": 0
        },
        {
            "func": "say",
            "syns": [
                "talked",
                "talk",
                "says",
                "say",
                "talks",
                "said",
                "talking",
                "saying"
            ],
            "jjrb": [
                "slow",
                "quick"
            ],
            "show": 0
        },
        {
            "func": "run",
            "syns": [
                "works",
                "working",
                "worked",
                "running",
                "runs",
                "work",
                "ran",
                "run"
            ],
            "jjrb": [
                "slow",
                "quick"
            ],
            "show": 1
        }
    ],
    "objects": [
        {
            "file": "ArtsyTree",
            "acts": {},
            "syns": [
                "ArtsyTree"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "BeachTerrain",
            "acts": {},
            "syns": [
                "BeachTerrain"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "birdnet",
            "acts": {},
            "syns": [
                "birdnet"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "child",
            "acts": {},
            "syns": [
                "child"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "CoffeeTable",
            "acts": {},
            "syns": [
                "CoffeeTable"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "cornfield",
            "acts": {},
            "syns": [
                "cornfield"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "daawat",
            "acts": {},
            "syns": [
                "daawat"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "farming_at_nubra",
            "acts": {},
            "syns": [
                "farming_at_nubra"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": ""
        },
        {
            "file": "lady",
            "acts": {
                "run": {
                    "fstart": 1,
                    "flast": -1
                }
            },
            "syns": [
                "lady"
            ],
            "jjrb": [],
            "move": [
                "move",
                "locate",
                "vanish"
            ],
            "joint": "makehuman_cmumb"
        }
    ],
    "logicals": [
        {
            "basic": "camera looks",
            "addon": [
                "camera looks #1-#30 @(0.9,-60,23.3,0,0,0,1,1,1)",
                "camera looks #31-#90 @(0.9,-60,23.3,0,0,0,1,1,1)-@(-9.2,-60,4.4,0,0,0,1,1,1)",
                "camera looks #121-#180 @(-9.2,-60,4.4,0,0,0,1,1,1)-@(-0.7,-60,-16.7,0,0,0,1,1,1)",
                "camera looks #190-#210 @(-0.7,-60,-16.7,0,0,0,1,1,1)-@(0,-120,0,0,0,0,1,1,1)"
            ]
        },
        {
            "basic": "lady is sulking",
            "addon": [
                "lady is running #1-#30 @(6.2,0,23.4,180,0,0,1,1,1)-@(0.9,0,23.7,180,0,0,1,1,1)",
                "lady is running #31-#150 @f(Y_totalrun)",
                "lady is running #151-#180 @(-0.7,0,-16.7,0,0,0,1,1,1)-@(7.8,0,-16.7,0,0,0,1,1,1)",
                "lady is running #181-#184 @(7.8,0,-16.7,0,0,0,1,1,1)-@(8.8,2,-15,0,0,0,1,1,1)"
            ]
        }
    ],
    "namedetail": "Basic environment for create at C:/ProgramData/Memeer/demo self initialized",
    "functions": {}
}