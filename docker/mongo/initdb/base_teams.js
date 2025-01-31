let now = new Date();
db['base_teams'].insertMany([
    {
        "team_id": "shambling-undead",
        "name": "Shambling Undead",
        "reroll_value": "70.000",
        "characters": [
            {
                "name": "Skeleton Lineman",
                "type": "skeleton-lineman",
                "max": 12,
                "value": "40,000",
                "stats": {
                    "MA": "5",
                    "ST": "3",
                    "AG": "4+",
                    "PA": "6+",
                    "AV": "8+"
                },
                "perks": [
                    "perk-regeneration",
                    "perk-thick-skull"
                ],
                "image": "shambling/skeleton.png",
                "tag_image": "shambling/skeleton_tag.png"
            },
            {
                "name": "Zombie Lineman",
                "type": "zombie-lineman",
                "max": 12,
                "value": "40,000",
                "stats": {
                    "MA": "4",
                    "ST": "3",
                    "AG": "4+",
                    "PA": "-",
                    "AV": "9+"
                },
                "perks": [
                    "perk-regeneration"
                ],
                "image": "shambling/zombie.png",
                "tag_image": "shambling/zombie_tag.png"
            },
            {
                "name": "Ghoul Runner",
                "type": "ghoul-runner",
                "max": 4,
                "value": "75,000",
                "stats": {
                    "MA": "7",
                    "ST": "3",
                    "AG": "3+",
                    "PA": "4+",
                    "AV": "8+"
                },
                "perks": [
                    "perk-dodge",
                ],
                "image": "shambling/ghoul.png",
                "tag_image": "shambling/ghoul_tag.png"
            },
            {
                "name": "Wight Blitzer",
                "type": "wight-blitzer",
                "max": 2,
                "value": "90,000",
                "stats": {
                    "MA": "6",
                    "ST": "3",
                    "AG": "3+",
                    "PA": "4+",
                    "AV": "9+"
                },
                "perks": [
                    "perk-regeneration",
                    "perk-block"
                ],
                "image": "shambling/wight.png",
                "tag_image": "shambling/wight_tag.png"
            },
            {
                "name": "Mummy",
                "type": "mummy",
                "max": 2,
                "value": "125,000",
                "stats": {
                    "MA": "3",
                    "ST": "5",
                    "AG": "5+",
                    "PA": "-",
                    "AV": "10+"
                },
                "perks": [
                    "perk-regeneration",
                    "perk-mighty-blow:1", //modifier to be added to the dice roll: i.e. Mighty Blow (1+)
                ],
                "image": "shambling/mummy.png",
                "tag_image": "shambling/mummy_tag.png"
            }
        ],
        "wallpaper": "shambling/wallpaper.png",
        "icon": "shambling/icon.png"
    },
    {
        "team_id": "lizardmen",
        "name": "Lizardmen",
        "reroll_value": "70.000",
        "characters": [
            {
                "name": "Skink Runner Lineman",
                "type": "skink-runner-lineman",
                "max": 12,
                "value": "60,000",
                "stats": {
                    "MA": "8",
                    "ST": "2",
                    "AG": "3+",
                    "PA": "4+",
                    "AV": "8+"
                },
                "perks": [
                    "perk-dodge",
                    "perk-stunty"
                ],
                "image": "lizardmen/lineman.png",
                "tag_image": "lizardmen/lineman.png"
            },
            {
                "name": "Chameleon Skink",
                "type": "chameleon-skink",
                "max": 2,
                "value": "70,000",
                "stats": {
                    "MA": "7",
                    "ST": "2",
                    "AG": "3+",
                    "PA": "3+",
                    "AV": "8+"
                },
                "perks": [
                    "perk-dodge",
                    "perk-stunty",
                    "perk-on-the-ball",
                    "perk-shadowing"
                ],
                "image": "lizardmen/chameleon.png",
                "tag_image": "lizardmen/chameleon_tag.png"
            },
            {
                "name": "Saurus Blocker",
                "type": "saurus-blocker",
                "max": 6,
                "value": "85,000",
                "stats": {
                    "MA": "6",
                    "ST": "4",
                    "AG": "5+",
                    "PA": "6+",
                    "AV": "10+"
                },
                "perks": [],
                "image": "lizardmen/saurusl.png",
                "tag_image": "lizardmen/saurus_tag.png"
            },
            {
                "name": "Kroxigor",
                "type": "kroxigor",
                "max": 1,
                "value": "140,000",
                "stats": {
                    "MA": "6",
                    "ST": "5",
                    "AG": "5+",
                    "PA": "-",
                    "AV": "10+"
                },
                "perks": [
                    "perk-bone-head",
                    "perk-loner:4",
                    "perk-mighty-blow:1",
                    "perk-prehensile-tail",
                    "perk-thick-skull"
                ],
                "image": "lizardmen/kroxigor.png",
                "tag_image": "lizardmen/kroxigor_tag.png"
            }
        ],
        "wallpaper": "lizardmen/wallpaper.png",
        "icon": "lizardmen/icon.png"
    }
]);