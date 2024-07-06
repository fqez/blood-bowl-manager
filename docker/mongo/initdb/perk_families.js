let now = new Date();
db['perk_families'].insertMany([
    {
        "family": "General",
        "items": [
            {
                "name": {
                    "en": "Dauntless",
                    "es": "Agallas"
                },
                "family": "General",
                "description": {
                    "en": "A player with this skill is capable of psyching himself up so he can take on even the very strongest opponent. The skill only works when the player attempts to block an opponent who is stronger than himself. When the skill is used, the coach of the player with the Dauntless skill rolls a D6 and adds it to his strength. If the total is equal to or lower than the opponent\u2019s Strength, the player must block using his normal Strength. If the total is greater, then the player with the Dauntless skill counts as having a Strength equal to his opponent\u2019s when he makes the block. The strength of both players is calculated before any defensive or offensive assists are added but after all other modifiers.",
                    "es": "Cuando el jugador realiza una acci\u00f3n de Placaje, incluido el Blitz, si el rival objetivo tiene m\u00e1s Fuerza que el jugador antes de aplicar modificadores por apoyos, tira 1d6 y a\u00f1ade la Fuerza del jugador, si el total es superior a la Fuerza del rival objetivo, el jugador aumenta su Fuerza hasta igualar la del rival durante este Placaje, despu\u00e9s deben aplicarse los apoyos. En caso de que el jugador tenga la habilidad como Furia, que le permite hacer dos Placajes, debe tirar Agallas por cada uno de ellos."
                }
            },
            {
                "name": {
                    "en": "Wrestle",
                    "es": "Forcejeo"
                },
                "family": "General",
                "description": {
                    "en": "The player is specially trained in grappling techniques. This player may use Wrestle when he blocks or is blocked and a !Both Down\u2019 result on the Block dice is chosen by either coach. Instead of applying the \u2018Both Down\u2019 result, both players are wrestled to the ground. Both players are Placed Prone in their respective squares even if one or both have the Block skill. Do not make Armour rolls for either player. Use of this skill does not cause a turnover unless the active player was holding the ball.",
                    "es": "Este jugador puede usar esta habilidad con el resultado de \u00abAmbos Derribados\u00bb, en lugar de aplicarlo normalmente, ambos jugadores se tumban en el suelo boca arriba, sin necesidad de tirar Armadura. No causa cambio de turno."
                }
            },
            {
                "name": {
                    "en": "Frenzy",
                    "es": "Furia"
                },
                "family": "General",
                "description": {
                    "en": "A player with this skill is a slavering psychopath who attacks his opponents in an uncontrollable rage. Unless otherwise overridden, this skill must always be used. When making a block, a player with this skill must always follow up if he can. If a \u2018Pushed\u2019 or \u2018Defender Stumbles\u2019 result was chosen, the player must immediately throw a second block against the same opponent so long as they are both still standing and adjacent. If possible, the player must also follow up this second block. If the frenzied player is performing a Blitz Action then he must pay a square of Movement and must make the second block unless he has no further normal movement and cannot Go For It again.",
                    "es": "Cada vez que este jugador realice una acci\u00f3n de Placaje (sola o como parte de una acci\u00f3n Blitz), debe realizar un seguimiento si el objetivo es empujado hacia atr\u00e1s y si puede hacerlo. Si el objetivo sigue en pie despu\u00e9s de ser empujado hacia atr\u00e1s, y si este jugador fue capaz de realizar el seguimiento, este jugador debe entonces realizar una segunda acci\u00f3n de Placaje contra el mismo objetivo, de nuevo ocupando a casilla del objetivo empujado hacia atr\u00e1s. Si este jugador realiza una acci\u00f3n Blitz, realizar una segunda acci\u00f3n de Placaje tambi\u00e9n le costar\u00e1 uno de Movimiento. Si a este jugador no le queda Movimiento para realizar una segunda acci\u00f3n de Placaje, deber\u00e1 Precipitarse para hacerlo. Si no puede correr, no puede realizar una segunda acci\u00f3n de Placaje. Ten en cuenta que si un jugador contrario en posesi\u00f3n del bal\u00f3n es empujado hacia tu Zona de Touch Down y sigue en pie, se marcar\u00e1 un touchdown, finalizando la entrada. En este caso, la segunda acci\u00f3n de Placaje no se realiza. Un jugador con esta habilidad no puede tener tambi\u00e9n la habilidad Apartar."
                }
            },
            {
                "name": {
                    "en": "Dirty Player",
                    "es": "Jugar Sucio"
                },
                "family": "General",
                "description": {
                    "en": "A player with this skill has trained long and hard to learn every dirty trick in the book. Add 1 to any Armour roll or Injury roll made by a player with this skill when they make a Foul as part of a Foul Action. Note that you may only modify one of the dice rolls, so if you decide to use Dirty Player to modify the Armour roll, you may not modify the Injury roll as well.",
                    "es": "(Dirty Player) Cuando este jugador comete una Falta, puede a\u00f1adir (+X) a la tirada de Armadura o Heridas."
                }
            },
            {
                "name": {
                    "en": "Sure Hands",
                    "es": "Manos Seguras"
                },
                "family": "General",
                "description": {
                    "en": "A player with the Sure Hands skill is allowed to re-roll the D6 if he fails to pick up the ball. In addition, the Strip Ball skill will not work against a player with this skill.",
                    "es": "(Sure Hands) El jugador puede repetir una tirada fallida de AG al intentar recoger el bal\u00f3n del suelo. Adem\u00e1s, el rival no puede usar Robar Bal\u00f3n."
                }
            },
            {
                "name": {
                    "en": "Kick",
                    "es": "Patada"
                },
                "family": "General",
                "description": {
                    "en": "The player is an expert at kicking the ball and can place the kick with great precision. In order to use this skill the player must be set up on the pitch when his team kicks off. The player may not be set up in either wide zone or on the line of scrimmage. Only if all these conditions are met is the player then allowed to take the kick-off. Because his kick is so accurate, you may choose to halve the number of squares that the ball scatters on kick-off, rounding any fractions down (i.e., 1 = 0, 2-3 = 1, 4- 5 = 2, 6 = 3).",
                    "es": "Si este jugador es elegido como el jugador que da la Patada Inicial, puede elegir reducir a la mitad el n\u00famero de casillas que se desv\u00eda el bal\u00f3n, redondeando hacia abajo."
                }
            },
            {
                "name": {
                    "en": "Shadowing",
                    "es": "Perseguir"
                },
                "family": "General",
                "description": {
                    "en": "The player may use this skill when a player performing an Action on the opposing team moves out of any of his tackle zones for any reason. The opposing coach rolls 2D6 adding his own player\u2019s movement allowance and subtracting the Shadowing player\u2019s movement allowance from the score. If the final result is 7 or less, the player with Shadowing may move into the square vacated by the opposing player. He does not have to make any Dodge rolls when he makes this move, and it has no effect on his own movement in his own turn. If the final result is 8 or more, the opposing player successfully avoids the Shadowing player and the Shadowing player may not move into the vacated square. A player may make any number of shadowing moves per turn. If a player has left the tackle zone of several players that have the Shadowing skill, then only one of the opposing players may attempt to shadow him.",
                    "es": "Este jugador puede usar esta habilidad cuando un oponente abandona voluntariamente su zona de defensa. Tira 1d6 y suma el MO del jugador, restando el MO del rival, si la diferencia es 6+, el jugador puede ocupar inmediatamente la casilla abandonada por el rival, sin necesidad de hacer tirada de esquivar alguna. El jugador puede usar esta habilidad m\u00faltiples veces por turno, pero s\u00f3lo un jugador puede usarla si hay varios con posibilidad de hacerlo."
                }
            },
            {
                "name": {
                    "en": "Tackle",
                    "es": "Placaje Defensivo"
                },
                "family": "General",
                "description": {
                    "en": "Opposing players who are standing in any of this player\u2019s tackle zones are not allowed to use their Dodge skill if they attempt to dodge out of any of the player\u2019s tackle zones, nor may they use their Dodge skill if the player throws a block at them and uses the Tackle skill.",
                    "es": "Cuando un jugador rival intenta esquivar desde la zona de defensa de este jugador, el rival no puede usar su habilidad Esquivar. Adem\u00e1s, cuando un rival es objetivo de un Placaje, o Blitz tampoco puede usarla."
                }
            },
            {
                "name": {
                    "en": "Block",
                    "es": "Placar"
                },
                "family": "General",
                "description": {
                    "en": "A player with the Block skill is proficient at knocking opponents down. The Block skill, if used, affects the results rolled with the Block dice, as explained in the Blocking rules.",
                    "es": "Si durante un placaje se obtiene el resultado de Ambos Derribados, el jugador puede ignorar este resultado."
                }
            },
            {
                "name": {
                    "en": "Pro",
                    "es": "Profesional"
                },
                "family": "General",
                "description": {
                    "en": "A player with this skill is a hardened veteran. Such players are called professionals or Pros by other Blood Bowl players because they rarely make a mistake. Once per turn, a Pro is allowed to re-roll any one dice roll he has made other than Armour, Injury or Casualty, even if he is Prone or Stunned. However, before the re-roll may be made, his coach must roll a D6. On a roll of 4, 5 or 6 the re-roll may be made. On a roll of 1, 2 or 3 the original result stands and may not be re-rolled with a skill or team re-roll; however you can re-roll the Pro roll with a Team re-roll.",
                    "es": "Durante su activaci\u00f3n este jugador puede intentar Repetir un \u00fanico dado, incluso si forma parte de un grupo de dados, excepto tiradas de Armadura, Heridas o lesiones. Tira un D6: \u2013 3+, el dado elegido puede ser repetido. \u2013 1-2, el dado no se puede repetir. Una vez usada esta habilidad, ya no se puede usar Re-Roll para esta tirada."
                }
            },
            {
                "name": {
                    "en": "Strip Ball",
                    "es": "Robar Bal\u00f3n"
                },
                "family": "General",
                "description": {
                    "en": "When a player with this skill blocks an opponent with the ball, applying a !Pushed\u2019 or !Defender Stumbles\u2019 result will cause the opposing player to drop the ball in the square that they are pushed to, even if the opposing player is not Knocked Down.",
                    "es": "(Strip Ball) Cuando este jugador elige como objetivo a un rival en posesi\u00f3n del bal\u00f3n como acci\u00f3n de Placaje o Blitz, puede obligar a soltar el bal\u00f3n en caso de obtener un resultado de empuj\u00f3n. El bal\u00f3n rebotar\u00e1 desde la casilla en la que se empuja al rival como si fuese tumbado."
                }
            },
            {
                "name": {
                    "en": "Fend",
                    "es": "Zafarse"
                },
                "family": "General",
                "description": {
                    "en": "This player is very skilled at holding off would-be attackers. Opposing players may not follow-up blocks made against this player even if the Fend player is Knocked Down. The opposing player may still continue moving after blocking if he had declared a Blitz Action.",
                    "es": "Si este jugador es empujado hacia atr\u00e1s como consecuencia de cualquier resultado de dados de Placaje que se aplique contra \u00e9l, puede elegir impedir que el jugador que le empuj\u00f3 hacia atr\u00e1s le siga. Sin embargo, el jugador que le hizo retroceder puede continuar movi\u00e9ndose como parte de una acci\u00f3n Blitz si le queda Movimiento. La habilidad no puede usarse cuando este jugador es empujado en cadena, contra un jugador con el rasgo de Bola y Cadena o contra un jugador con la habilidad Imparable que realiz\u00f3 la acci\u00f3n de Placaje como parte de un Blitz."
                }
            }
        ]
    },
    {
        "family": "Extraordinary",
        "items": [
            {
                "name": {
                    "en": "Drunkard",
                    "es": "Borracho"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "This player suffers a -1 penality to the dice roll when attempting to Rush.",
                    "es": "Este jugador sufre una penalizaci\u00f3n de -1 a la tirada de dados cuando intenta precipitarse. (A Por Ellos)"
                }
            },
            {
                "name": {
                    "en": "Hit and Run",
                    "es": "Golpear y correr"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "After a player with this Trait performs a Block action, they may immediately move one free square ignoring Tackle Zones so long as they are still Standing. They must ensure that after this free move, they are not Marked by or Marking any opposition players.",
                    "es": "(Hit and Run) Despu\u00e9s de que un jugador con este rasgo realice una acci\u00f3n de Placar, puede moverse inmediatamente en una casilla libre ignorando las zonas de placaje mientras siga en pie. Deben asegurarse de que, tras este movimiento libre, no son marcados por ning\u00fan jugador rival."
                }
            },
            {
                "name": {
                    "en": "Animal Savagery",
                    "es": "Animal Feroz"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before peforming the action, roll a D6, applying a +2 modifier to the dice roll if you declared the player would perform a Block or Blitz action (or a Special action granted by a Skill or Trait that can be performed instead of a Block action): If you declared that this player would perform an action which can only be performed once per team turn and this player\u2019s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                    "es": "(Animal Savagery) Cuando se activa a este jugador y se declara una acci\u00f3n, incluso si est\u00e1 tumbado o sin zona de defensa, debe tirar 1d6, sumando +2 si la acci\u00f3n declarada es Placaje, Blitz o Habilidad Especial que sustituya al Placaje. \n1-3, Un jugador amigo en pie y adyacente, se tumba boca arriba, no causa cambio de turno a menos que llevase el bal\u00f3n. Despu\u00e9s debe tirar contra su Armadura, el rival puede usar a su gusto cualquier habilidad aplicable que posea.Una vez resuelto esto puede continuar ejecutando su acci\u00f3n declarada normalmente.Si no hay jugador amigo en pie y adyacente, el jugador perder\u00e1 su acci\u00f3n declarada y perder\u00e1 su zona de defensa. Si no hay jugador amigo en pie y adyacente, el jugador perder\u00e1 su acci\u00f3n declarada y perder\u00e1 su zona de defensa. 4+, el jugador contin\u00faa su acci\u00f3n normalmente. Si declaraste que este jugador realizar\u00eda una acci\u00f3n que s\u00f3lo puede realizarse una vez por turno de equipo y la activaci\u00f3n de este jugador termin\u00f3 antes de que la acci\u00f3n pudiera completarse, la acci\u00f3n se considera realizada y ning\u00fan otro jugador de tu equipo puede realizar la misma acci\u00f3n este turno de equipo."
                }
            },
            {
                "name": {
                    "en": "Animosity",
                    "es": "Animosidad"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "This player is jealous of and dislikes certain other players of their team, as shown in brackets after the name of the Skill on this player\u2019s profile. This may be defined by position or race. For example, a Skaven Thrower on an Underworld Denizens team has Animosity (Underworld Goblin Lineman), meaning they suffer Animosity towards any Underworld Goblin Lineman players on their team, Whereas a Skaven Renegade on a Chaos Renegade team has Animosity (all team-mates), meaning they suffer Animosity towards all of their team-mates equally. When this player wishes to perform a Hand-off action to a team-mate of the type listed, or attempts to perform a Pass action and the target square is occupied by a team-mate of the type listed, this player may refuse to do so. Roll a D6. On a roll of 1, this player refuses to perform the action and their activation comes to an end. Animosity does not extend to Mercenaries or Star Players.",
                    "es": "Cuando este jugador desea hacer una Entrega en Mano o un Pase a un jugador listado en (x), debe tirar 1D6, con un resultado de 1 el jugador se queda con el bal\u00f3n y termina su activaci\u00f3n. No se aplica a Mercenarios ni a Jugadores Estrella."
                }
            },
            {
                "name": {
                    "en": "Stab",
                    "es": "Apu\u00f1alar"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "Instead of performing a Block action (on its own or as part of a Blitz action), this player may perform a \u2018Stab\u2019 Special action. Exactly as described for a Block action, nominate a single Standing player to be the target of the Stab Special action. There is no limit to how many players with this Trait may perform this Special action each team turn.To perform a Stab Special action, make an unmodified Armour roll against the target: \nIf the Armour of the player hit is broken, they become Prone and an Injury roll is made against them, This Injury roll cannot be modified in any way. If the Armour of the player hit is not broken, this Trait has no effect. If Stab is used as part of a Blitz action, the player cannot continue moving after using it.",
                    "es": "En lugar de realizar una acci\u00f3n de Placaje o Blitz, puede elegir un oponente y hacer esta acci\u00f3n especial, debe tirar por Armadura y Heridas normalmente, ninguna de estas tiradas puede ser modificada de ninguna manera, si no supera la tirada de Armadura, no tiene efecto. Si forma parte de un Blitz no puede seguir moviendo."
                }
            },
            {
                "name": {
                    "en": "Secret Weapon",
                    "es": "Arma Secreta"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When a drive in which this player took part ends, even if this player was not on the pitch at the end of the drive, this player will be Sent-off for committing a Foul, as described on page 63.",
                    "es": "(Secret Weapon) Cuando termine la entrada en la que este jugador haya participado, incluso si ya no se encuentra en el campo al finalizar dicha entrada, este jugador ser\u00e1 expulsado por el \u00e1rbitro como si hubiera cometido una Falta."
                }
            },
            {
                "name": {
                    "en": "Titchy",
                    "es": "Canijo"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "This player may apply a +1 modifier to any Agility tests they make in order to Dodge. However, if an opposition player dodges into a square within the Tackle Zone of this player, this player does not count as Marking the moving player for the purpose of calculating Agility test modifiers.",
                    "es": "Este jugador puede aplicar un +1 a la tirada de AG al Esquivar, adem\u00e1s cuando un oponente intenta Esquivar a una zona de defensa de un jugador con esta habilidad no aplica modificadores negativos de AG al esquivarle."
                }
            },
            {
                "name": {
                    "en": "Swarming",
                    "es": "Colarse"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "During each Start of Drive sequence, after Step 2 but before Step 3, you may remove D3 players with this Trait from the Reserves box of your dugout and set them up on the pitch, allowing you to set up more than the usual 11 players. These extra players may not be placed on the Line of Scrimmage or in a Wide Zone. Swarming players must be set up in their team\u2019s half.When using Swarming, a coach may not set up more players with the Swarming trait onto the pitch than the number of friendly players with the Swarming trait that were already set up. So, if a team had 2 players with the Swarming trait already set up on the pitch, and then rolled for 3 more players to enter the pitch via Swarming, only a maximum of 2 more Swarming players could be set up on the pitch.",
                    "es": "Durante el inicio de cada entrada, despu\u00e9s del paso 2 (Colocar el Bal\u00f3n y Desviar) pero antes del paso 3 (Tirar la tabla de Patada Inicial), puedes retirar 1d3 jugadores con esta regla del banquillo de reservas y colocarlos en el campo, superando el l\u00edmite de 11 jugadores en el campo, no pueden estar en las bandas ni en la l\u00ednea frontal central."
                }
            },
            {
                "name": {
                    "en": "Kick Team-mate",
                    "es": "Chutar Compa\u00f1ero"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "Once per team turn, in addition to another player performing either a Pass or a Throw Team-mate action, a single player with this Traits on the active team can perform a \u2018Kick Team-mate\u2019 Special action, follow the rules for Throw Team-mates actions as described on page 52.However, if the Kick Team-mate Special action is fumbled, the kicked player is automatically removed from play and an injury roll is made against them, treating a Stunned result as a KO\u2019d result (note that, if the player that performed this action also has the Mighty Blow (+x) skill, the coach of the opposing team may use that Skill on this Injury roll). If the kicked player was in possession of the ball when removed from play, the ball will bounce from the square they occupied.",
                    "es": "(Kick Team-mate) Una vez por turno, adem\u00e1s de que otro jugador realice una acci\u00f3n de Pase o Lanzar Compa\u00f1ero, este jugador puede efectuar un Chutar Compa\u00f1ero. Para efectuarlo debes seguir las mismas reglas que con el Lanzar Compa\u00f1ero, pero si el resultado del Lanzamiento es un fumble, el jugador Pateado realiza tirada de Heridas, considerando el KO como resultado m\u00ednimo, adem\u00e1s el entrenador rival puede hacer uso del Golpe Mort\u00edfero del Pateador si lo tuviera."
                }
            },
            {
                "name": {
                    "en": "Decay",
                    "es": "Descomposici\u00f3n"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "If this player suffers a Casualty result on the injury table, there is a +1 modifier applied to all rolls made against this player on the Casualty table.",
                    "es": "Cuando este jugador tira en la tabla de Lesiones debe sumar +1 a dicha tirada."
                }
            },
            {
                "name": {
                    "en": "Take Root",
                    "es": "Echar Ra\u00edces"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When this player is activated, even if they are Prone or have lost theio Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6: \nOn a roll of 1, this player becomes \u2018Rooted\u2019:A Rooted player cannot move from the square they currently occupy for any reason, voluntarily or otherwise, until the end of this drive, or until they are Knocked Down or Placed Prone.A Rooted player may perform any action available to them provided they can do so without moving. For example, a Rooted player may perform a Pass action but may not move before making the pass, and so on. A Rooted player cannot move from the square they currently occupy for any reason, voluntarily or otherwise, until the end of this drive, or until they are Knocked Down or Placed Prone. A Rooted player may perform any action available to them provided they can do so without moving. For example, a Rooted player may perform a Pass action but may not move before making the pass, and so on. On a roll of 2+, this player continues their activation as normal. If you declared that this player would perform any action that includes movement (Pass, Hand-off, Blitz or Foul) prior to them becoming Rooted, they may, complete the action if possible. If they cannot, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                    "es": "(Take Root) Cuando se activa a este jugador y se declara una acci\u00f3n, incluso si est\u00e1 tumbado o sin zona de defensa, debe tirar 1D6: \n1,\u00a0el jugador quedar\u00e1 enraizado, no podr\u00e1 abandonar la casilla en la que se encontrase hasta el final de esta entrada, a menos que sea tumbado en el suelo. Un jugador enraizado puede realizar cualquier acci\u00f3n que no implique moverse. Cualquier acci\u00f3n declarada antes de enraizarse se considera realizada aunque no se lleve a cabo. 2+,\u00a0el jugador contin\u00faa su acci\u00f3n normalmente."
                }
            },
            {
                "name": {
                    "en": "Trickster",
                    "es": "Embaucador"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When a player is about to be hit by a Block action or a Special action that replaces a Block action (with the exception of a Block action caused by the Ball & Chain Move Special action), before determinig how many dice are rolled, they may be removed from the pitch ans placed in any other unoccupied square adjacent to the player performing the Block action.. The Block action then takes place as normal. If the player using this Trait is holding the ball and places themselves inthe opposition End Zone, the Block action will still be fully resolved before any touchdown is resolved.",
                    "es": "Cuando un jugador est\u00e1 a punto de ser golpeado por una acci\u00f3n de Placaje o una acci\u00f3n que sustituye a una acci\u00f3n de Placaje (con la excepci\u00f3n de una acci\u00f3n de Placaje causada por la acci\u00f3n Especial de Movimiento de Bola con Cadena), antes de determinar cu\u00e1ntos dados se tiran, puede ser retirado del terreno de juego y colocado en cualquier otra casilla desocupada adyacente al jugador que realiza la acci\u00f3n de Placaje. Despues la acci\u00f3n de Placaje se realiza de forma normal. Si el jugador que utiliza este Rasgo tiene el bal\u00f3n en su poder y se coloca en la zona de TouchDown contraria, la acci\u00f3n de Bloqueo se resolver\u00e1 por completo antes de que se resuelva cualquier TouchDown."
                }
            },
            {
                "name": {
                    "en": "Stunty",
                    "es": "Escurridizo"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When this player makes an Agility test in order to Dodge, they ignore any -1 modifiers for being Marked in the square they have moved into, unless they also have either the Bombardier trait, the Chainsaw trait or the Swoop trait.However, when an opposition player attempts to interfere with a Pass action performed by this player, that player may apply a +1 modifier to their Agility test.Finally, player with this Trait are more prone to injury. Therefore, when an Injury roll is made against this player, roll 2D6 and consult the Stunty Injury table, on page 60.\u00a0This Trait may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                    "es": "Cuando este jugador hace una tirada de AG para Esquivar, puede ignorar todos los modificadores negativos por zonas de defensa enemigas, a menos que tenga la habilidad Bombardero, Motosierra o Planear. Adem\u00e1s, cuando un rival intenta interferir un Pase hecho por este jugador, puede aplicar un +1 a la tirada de AG. Tambi\u00e9n deben usar la Tabla de Heridas para Escurridizos."
                }
            },
            {
                "name": {
                    "en": "Stakes",
                    "es": "Estacas"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "This player is armed with special stakes that are blessed to cause extra damage to the Undead and those that work with them. This player may add 1 to the Armour roll when they make a Stab attack against any player playing for a Khemri, Necromantic, Undead or Vampire team.",
                    "es": "El jugador est\u00e1 armado con unas estacas especiales que est\u00e1n bendecidas para causar un da\u00f1o adicional a los No Muertos y a aqu\u00e9llos que trabajan para ellos. El jugador puede a\u00f1adir 1 a la tirada de Armadura cuando realice un ataque con Pu\u00f1al contra cualquier jugador que juegue para un equipo Khemri, Nigromantes, No Muertos o Vampiros."
                }
            },
            {
                "name": {
                    "en": "Bone Head",
                    "es": "Est\u00fapido"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6: \nOn a roll of 1, this player forgets what they are doing and their activation ends immediately. Additionally, this player loses their Tackle Zone until they are next activated. On a roll of 2+, this player continues their activation as normal and completes their declared action. If you declared that this player would perform an action which can only be performed once per team turn and this player\u2019s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                    "es": "(Bone Head) Cuando se activa a este jugador y se declara una acci\u00f3n, incluso si est\u00e1 tumbado o sin zona de defensa, debe tirar 1d6: \u2013\u00a01,\u00a0el jugador perder\u00e1 su acci\u00f3n declarada y perder\u00e1 su zona de defensa. \u2013\u00a02+,\u00a0el jugador contin\u00faa su acci\u00f3n normalmente."
                }
            },
            {
                "name": {
                    "en": "Fan Favorite",
                    "es": "Favorito del P\u00fablico"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "The fans love seeing this player on the pitch so much that even the opposing fans cheer for your team. For each player with Fan Favourite on the pitch your team receives an additional +1 FAME modifier (see page 18) for any Kick-Off table results, but not for the Winnings roll.",
                    "es": "(Fan Favorite) Los hinchas adoran tanto ver a este jugador sobre el terreno de juego que incluso los hinchas contrarios animan a tu equipo. Por cada jugador Favorito del P\u00fablico de tu equipo que se encuentra en el campo, tu equipo recibe un +1 adicional al modificador de FAMA para cualquier resultado de la Tabla de Patada Inicial, pero no para la tirada de Recaudaci\u00f3n."
                }
            },
            {
                "name": {
                    "en": "Right Stuff",
                    "es": "Humanoide Bala"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "If this player also has a Strength characteristic of 3 or less, they can be thrown by a team-mate with the Throw Team-mate skill, as described on page 52.\u00a0This Trait may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                    "es": "(Right Stuff) Si este jugador tiene FU 3 o inferior puede ser Lanzado por un Compa\u00f1ero de Equipo."
                }
            },
            {
                "name": {
                    "en": "Unchannelled Fury",
                    "es": "Ira Descontrolada"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6, applying a +2 modifier to the dice roll if you declared the player would perform a Block or Blitz action (or a Special action granted by a Skill or Trait that can be performed instead of a Block action) \nOn a roll of 1-3, this player rages incoherently at others but achieves little else. Their activation ends immediately. On a roll of 4+, this player continues their activation as normal and completes their declared action. If you declared that this player would perform an action which can only be performed once per team turn and this player\u2019s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn. Take a look to all the teams on Blood Bowl!",
                    "es": "(Unchannelled Fury) Cuando se activa a este jugador y se declara una acci\u00f3n, incluso si est\u00e1 tumbado o sin zona de defensa, debe tirar 1d6, sumando +2 si la acci\u00f3n declarada es Placaje, Blitz o Habilidad Especial. \n1-3,\u00a0El jugador perder\u00e1 su acci\u00f3n declarada. *No pierde zona de defensa.* 4+,\u00a0el jugador contin\u00faa su acci\u00f3n normalmente."
                }
            },
            {
                "name": {
                    "en": "My Ball",
                    "es": "Mi Bal\u00f3n"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "A player with this Trait may not willingly give up the ball when in possession of it, and so may not make Pass actions, Hand-off actions, or use any other Skill or Trait that would allow them to relinquish possession of the ball. The only way they can lose possession of the ball is by being Knocked Down, Placed Prone, Falling Over or by the effect of a Skill, Trait or special rule of an opposing model.",
                    "es": "(My Ball) Un jugador con este Rasgo no puede ceder voluntariamente el bal\u00f3n cuando est\u00e1 en posesi\u00f3n del mismo, por lo que no puede realizar acciones de Pase, Acciones de Entrega, ni utilizar ninguna otra Habilidad o Rasgo que le permita renunciar a la posesi\u00f3n del bal\u00f3n. La \u00fanica forma de perder la posesi\u00f3n del bal\u00f3n es ser Derribado, Aturdido, Caerse o por el efecto de una Habilidad, Rasgo o regla especial de un jugador contrario."
                }
            },
            {
                "name": {
                    "en": "Hypnotic Gaze",
                    "es": "Mirada hipn\u00f3tica"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "The player has a powerful telepathic ability that he can use to stun an opponent into immobility. The player may use hypnotic gaze at the end of his Move Action on one opposing player who is in an adjacent square. Make an Agility roll for the player with hypnotic gaze, with a -1 modifier for each opposing tackle zone on the player with hypnotic gaze other than the victim\u2019s. If the Agility roll is successful, then the opposing player loses his tackle zones and may not catch, intercept or pass the ball, assist another player on a block or foul, or move voluntarily until the start of his next Action or the drive ends. If the roll fails, then the hypnotic gaze has no effect.",
                    "es": "(Hypnotic Gaze) Durante su activaci\u00f3n puede hacer una acci\u00f3n especial de Mirada Hipn\u00f3tica, declara el jugador en pie objetivo y en su zona de defensa, realiza una tirada de AG aplicando un -1 por cada zona de defensa enemiga. Si se supera la tirada el jugador pierde su zona de defensa hasta su siguiente activaci\u00f3n. Una vez usada esta habilidad finaliza la activaci\u00f3n del jugador. El jugador puede utilizar la Mirada Hipn\u00f3tica al final de su Acci\u00f3n de Movimiento."
                }
            },
            {
                "name": {
                    "en": "Chainsaw",
                    "es": "Motosierra"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "Instead of performing a Block action (on its own or as part of a Blitz action), this player may perform a \u201cChainsaw Attack\u201d Special action. Exactly as described for a Block action, nominate a single Standing player to be the target of the Chainsaw Attack Special action, There is no limit to how many players with this Trait may perform this Special action each team turn.To perform a Chainsaw Attack Special action, roll a D6: \nOn a roll of 2+, the nominated target is hit by Chainsaw! On a roll of 1, the Chainsaw will violently \u2018kick-back\u2019 and hit the player wielding it.\u00a0This will result in a Turnover. In either case, an Armour roll is made against the player hit by the Chainsaw, adding +3 to the result. If the armour of the player hit is broken, they become Prone and an Injury roll is made against them. This Injury roll cannot be modified in any way. If the armour of the player hit is not broken, this Trait has no effect This player can only use the Chainsaw once per turn (i.e., Chainsaw cannot be used with Frenzy or Multipe Block) and if used as part of a Blitz action, this player cannot continue moving after using it.If this player Fails Over or is Knocked Down, the opposing coach may add +3 to the Armour roll made against the player.If an opposition player performs a Block action targeting this player and a Player Down! or a POW! result is applied, +3 is added to the Armour roll. If a Both Down result is applied, +3 is added to both Armour rolls.Finally, this player may use their Chainsaw when they perform a Foul action. Roll a D6 for kick-back as described above. Once again, an Armour roll is made against the player hit by the Chainsaw. adding +3 to the score.",
                    "es": "En lugar de efectuar una acci\u00f3n de Placaje o Blitz, este jugador puede hacer una acci\u00f3n especial de Motosierra, declara el objetivo del ataque y tira 1d6: \n2+, el objetivo es impactado por la Motosierra. 1, el atacante es impactado a s\u00ed mismo con la Motosierra. El jugador impactado por la Motosierra debe hacer una tirada de Armadura aplicando un +3 a la tirada. Si se supera la tirada de Armadura, se hace la tirada de Heridas, que no puede ser modificada de ninguna manera. Si no se supera la tirada de Armadura, el ataque no tiene efecto. El jugador s\u00f3lo puede usar la Motosierra una vez por turno (no puede combinarse con Placaje M\u00faltiple o Furia) Si el ataque forma parte de un Blitz no podr\u00e1 continuar moviendo. Si un oponente realiza un placaje contra un jugador con Motosierra y resulta \u00abAtacante Derribado\u00bb puede sumar +3 a la tirada de Armadura, as\u00ed como si el resultado es \u00abAmbos Derribados\u00bb ambos aplican +3 a la tirada de Armadura. Si el jugador comete Falta sobre un oponente tira 1d6 para ver si se impacta a s\u00ed mismo, si no aplica el +3 a la tirada de Armadura."
                }
            },
            {
                "name": {
                    "en": "Swoop",
                    "es": "Planear"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "If this player is thrown by a team-mate, they do not scatter before landing as they normally would. Instead, you may place the Throw-in template over the player, facing towards either End Zone or either sideline as you wish. The player then moves from the target square D3 squares in a direction determined by rolling a D6 and referring to the Throw-in template.",
                    "es": "Cuando este jugador es Lanzado por un Compa\u00f1ero no se dispersa normalmente antes de aterrizar, en cambio debes colocar la plantilla de Devoluci\u00f3n de bal\u00f3n en direcci\u00f3n a la l\u00ednea de Touchdown o una de las Bandas y avanzar 1d3 casillas en la direcci\u00f3n aleatoria marcada por la plantilla."
                }
            },
            {
                "name": {
                    "en": "Pogo Stick",
                    "es": "Pogo Saltar\u00edn"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "During their movement, instead of jumping over a single square that is occupied by a Prone or Stunned player, as described on page 45, a player with this Trait may choose to Leap over any single adjacent square, including unoccupied square and squares occupied by Standing players. Additionally, when this player makes and Agility test to jump over a Prone or Stunned player, or to Leap over an empty square or a square occupied by a Standing player, they may ignore any negative modifiers that would normally be applied for being Marked in the square they jumped or leaped from and/or for being marked in the square they have jumped or leaped into. A player with this Trait cannot also have the Leap skill.",
                    "es": "(Pogo Stick) En lugar de intentar brincar a trav\u00e9s de jugadores tumbados, adem\u00e1s puede saltar a trav\u00e9s jugadores en pie, se realiza de igual forma, pero ignorando todos los penalizadores. Un jugador con esta habilidad no puede tener Saltar."
                }
            },
            {
                "name": {
                    "en": "Projectile Vomit",
                    "es": "Proyectil V\u00f3mito"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "Instead of performing a Block action (on its own or as part of a Blitz action), this player may perform a \u2018Projectile Vomit\u2019 Special action. Exactly as described for a Block action, nominate a single Standing player to be the target of the Projectile Vomit Special action. There is no limit to how many players with this Trait may perform this Special action each team turn.To perform a Projectile Vomit Special action, roll a D6: \nOn a roll of 2+, this player regurgitates acidic bile onto the nominated target. On a roll of 1, this player belches and snorts, before covering itself in acid bile. In either case, an armour roll is made against the player hit by the Projectile vomit. This Armour roll cannot be modified in any way. If the armour of the player hit is broken, they become Prone and an Injury roll is made against them. This Injury roll cannot be modified in any way. If the armour of the playerhit is not broken, this Trait has no effect. A player can only perform this Special action once per turn (i.e. Projectile Vomit cannot be used with Frenzy or Multiple Block).",
                    "es": "(Projectile Vomit) En lugar de realizar una acci\u00f3n de Placaje o Blitz, puede elegir un oponente y hacer esta acci\u00f3n especial. Tira 1d6: \n1,\u00a0el jugador se impacta a s\u00ed mismo. 2+,\u00a0el jugador oponente es impactado. En cualquier caso, el jugador impactado debe tirar por Armadura normalmente. Si se supera la tirada de Armadura el jugador es tumbado boca arriba y se debe tirar por Heridas. Ninguna de estas tiradas puede ser modificada de ninguna manera, sino supera la tirada de Armadura, no tiene efecto."
                }
            },
            {
                "name": {
                    "en": "Really Stupid",
                    "es": "Realmente Est\u00fapido"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6, applying a +2 modifier to the dice roll if this player is currently adjacent to one or more Standing team-mates that do not have this Trait: \nOn a roll of 1-3, this player forgets what they are doing and their activation ends immediately. Additionally, this player loses their Tackle Zone until they are next activated. On a roll of 4+, this player continues their activation as normal and completes their declared action. Note that if you declared that this player would perform an action which can only be performed once per team turn and this player\u2019s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                    "es": "(Really Stupid) Cuando se activa a este jugador y se declara una acci\u00f3n, incluso si est\u00e1 tumbado o sin zona de defensa, debe tirar 1d6, sumando +2 si est\u00e1 adyacente a un Compa\u00f1ero en pie que no sea Realmente Est\u00fapido tambi\u00e9n: \u2013\u00a01-3,\u00a0el jugador perder\u00e1 su acci\u00f3n declarada y perder\u00e1 su zona de defensa. \u2013 4+, el jugador contin\u00faa su acci\u00f3n normalmente."
                }
            },
            {
                "name": {
                    "en": "Regeneration",
                    "es": "Regeneraci\u00f3n"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "After a Casualty roll has been made against this player, roll a D6. On a roll of 4+, the Casualty roll is dicarded without effect and the player is placed in the Reserves box rather than the Casualty box of their team dugout. On a roll of 1-3, however, the result of the Casualty roll is applied as normal.\u00a0This Trait may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                    "es": "Si este jugador sufre una herida en la tabla de Lesiones, puedes ignorar el resultado con una tirada de 4+ exitosa. Si tiene \u00e9xito puedes poner al jugador en el banquillo en reservas."
                }
            },
            {
                "name": {
                    "en": "Always Hungry",
                    "es": "Siempre Hambriento"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "If this player wishes to perform a Throw Team-mate action, roll a D6 after they have finished moving, but before they throw their team-mate. On a roll of 2+, continue with the throw as normal. On a roll of 1, this player will attempt to eat their team-mate. Roll another D6: \nOn a roll of 1, the team-mate has been eaten and is immediately removed from the Team Draft list. No apothecary can save them and no Regeneration attempts can be made. If the team-mate was in possession of the ball, it will bounce from the square the player occupies. On a roll of 2+, the team-mate squirms free and the Throw Team-mate action is automatically fumbled, as described on page 53.",
                    "es": "(Always Hungry) Si este jugador desea Lanzar Compa\u00f1ero, tira 1d6 despu\u00e9s de que haya movido. Con 2+ contin\u00faa la acci\u00f3n normalmente, con un resultado de 1, tira otro d6: \u2013 1, se come al Compa\u00f1ero, no se puede usar M\u00e9dico ni regeneraci\u00f3n. Borra al jugador del Roster. \u2013\u00a02+,\u00a0el Compa\u00f1ero se escapa y el resultado del Lanzamiento es autom\u00e1ticamente un fumble."
                }
            },
            {
                "name": {
                    "en": "No Hands",
                    "es": "Sin Manos"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "The player is unable to pick up, intercept or carry the ball and will fail any catch roll automatically, either because he literally has no hands or because his hands are full. If he attempts to pick up the ball then it will bounce, and will cause a turnover if it is his team\u2019s turn.",
                    "es": "(No Hands) Este jugador no puede intentar coger el bal\u00f3n del suelo, atrapar o interferir un pase. Si lo hace falla autom\u00e1ticamente y rebotar\u00e1, adem\u00e1s causar\u00e1 p\u00e9rdida de turno si voluntariamente intenta cogerlo del suelo al entrar en la casilla del bal\u00f3n."
                }
            },
            {
                "name": {
                    "en": "Loner",
                    "es": "Solitario"
                },
                "family": "Extraordinary",
                "description": {
                    "en": "If this player wishes to use a team re-roll, roll a D6. If you roll equal to or higher than the target number show in brackets, this player may use the team re-roll as normal. Otherwise, the original result stands without being re-rolled but the team re-roll is lost just as if it had been used.\u00a0This Trait must still be used if the player is Prone or has lost their Tackle Zone.",
                    "es": "Si este jugador desea hacer uso de una Re-Roll de equipo debe primero superar una tirada de Solitario (x+), de lo contrario no podr\u00e1 repetir la tirada y perder\u00e1 esa Re-Roll que deseaba usar."
                }
            }
        ]
    },
    {
        "family": "Agility",
        "items": [
            {
                "name": {
                    "en": "Catch",
                    "es": "Atrapar"
                },
                "family": "Agility",
                "description": {
                    "en": "A player who has the Catch skill is allowed to re-roll the D6 if he fails a catch roll. It also allows the player to re-roll the D6 if he drops a hand-off or fails to make an interception.",
                    "es": "El jugador puede repetir una tirada fallida de AG al intentar atrapar un bal\u00f3n."
                }
            },
            {
                "name": {
                    "en": "Jump Up",
                    "es": "En Pie de un Salto"
                },
                "family": "Agility",
                "description": {
                    "en": "A player with this skill is able to quickly get back into the game. If the player declares any Action other than a Block Action he may stand up for free without paying the three squares of movement. The player may also declare a Block Action while Prone which requires an Agility roll with a +2 modifier to see if he can complete the Action. A successful roll means the player can stand up for free and block an adjacent opponent. A failed roll means the Block Action is wasted and the player may not stand up.",
                    "es": "(Jump Up) Si este jugador est\u00e1 en el suelo, puede levantarse sin gastar ning\u00fan punto de Movimiento, adem\u00e1s puede intentar hacer acci\u00f3n de Placaje desde el suelo (Sin gastar la acci\u00f3n de Blitz), debe superar una tirada de Agilidad con +1, si tiene \u00e9xito, el jugador se levanta y hace el Placaje normalmente, si no se queda tumbado en el suelo y pierde su acci\u00f3n. Esta Habilidad puede seguir us\u00e1ndose si el jugador est\u00e1 Tumbado o ha perdido su Zona de defensa."
                }
            },
            {
                "name": {
                    "en": "Sprint",
                    "es": "Esprintar"
                },
                "family": "Agility",
                "description": {
                    "en": "When this player performs any action that includes movement, they may attempt to Rush three times, rather than the usual two.",
                    "es": "Cuando este jugador realiza cualquier acci\u00f3n que incluye moverse, puede intentar Forzar la marcha hasta tres veces, en lugar de las dos habituales."
                }
            },
            {
                "name": {
                    "en": "Dodge",
                    "es": "Esquivar"
                },
                "family": "Agility",
                "description": {
                    "en": "A player with the Dodge skill is adept at slipping away from opponents, and is allowed to re-roll the D6 if he fails to dodge out of any of an opposing player\u2019s tackle zones. However, the player may only re-roll one failed Dodge roll per turn. In addition, the Dodge skill, if used, affects the results rolled on the Block dice, as explained in the Blocking rules.",
                    "es": "Una vez por turno de equipo, durante su activaci\u00f3n, este jugador puede repetir un chequeo de Agilidad fallido para intentar esquivar. Adem\u00e1s, este jugador puede usar su habilidad esquivar cuando sea blanco de una acci\u00f3n de Placaje (por si solo o como parte de un Blitz ) y se obtenga un resultado de \u00abDesequilibrio\u00bb contra el."
                }
            },
            {
                "name": {
                    "en": "Sneaky Git",
                    "es": "Furtivo"
                },
                "family": "Agility",
                "description": {
                    "en": "During a Foul Action a player with this skill is not ejected for rolling natural doubles on the Armour roll.",
                    "es": "(Sneaky Git) Cuando este jugador realiza una acci\u00f3n de falta, no es expulsado por sacar un doble natural en la tirada de armadura. Aun asi, podra ser expulsado si saca un doble natural en la tirada de herida."
                }
            },
            {
                "name": {
                    "en": "Sure Feet",
                    "es": "Pies Firmes"
                },
                "family": "Agility",
                "description": {
                    "en": "Once per team turn, during their activation, this player may re-roll the D6 when attempting to Rush.",
                    "es": "(Sure Feet) Una vez por turno de equipo, durante la activaci\u00f3n de este jugador, este jugador puede repetir la tirada al intentar Forzar la marcha."
                }
            },
            {
                "name": {
                    "en": "Diving Tackle",
                    "es": "Placaje Heroico"
                },
                "family": "Agility",
                "description": {
                    "en": "The player may use this skill after an opposing player attempts to dodge out of any of his tackle zones. The opposing player must subtract 2 from his Dodge roll for leaving the player\u2019s tackle zone. If a player is attempting to leave the tackle zone of several players that have the Diving Tackle skill, then only one of the opposing players may use Diving Tackle. Diving Tackle may be used on a re-rolled dodge if not declared for use on the first Dodge roll. Once the dodge is resolved but before any armour roll for the opponent (if needed), the Diving Tackle Player is Placed Prone in the square vacated by the dodging player but do not make an Armour or Injury roll for the Diving Tackle player.",
                    "es": "(Diving Tackle) Cuando un oponente obtiene un \u00e9xito en la tirada de Agilidad y abandona la zona de defensa del jugador al Esquivar, Saltar o Brincar, el jugador puede restar 2 a dicha tirada de Agilidad, este jugador se tumba en el suelo en la casilla abandonada, sin necesidad de tirada de Armadura. S\u00f3lo un jugador puede usar esta habilidad si hay varios con opci\u00f3n de hacerlo."
                }
            },
            {
                "name": {
                    "en": "Safe Pair of Hands",
                    "es": "Proteger el Cuero"
                },
                "family": "Agility",
                "description": {
                    "en": "If this player is Knocked Down or Placed Prone (but not it they Fall Over) whilst in possession of the ball, the ball does not bounce. Instead, you may place the ball in an unoccupied square adjacent to the one this player occupies when they become Prone.\u00a0This Skill may still be used if the player is Prone.",
                    "es": "(Safe Pair of Hands) Si este jugador es derribado o colocado boca abajo (pero no si se cae) mientras est\u00e1 en posesi\u00f3n del bal\u00f3n, el bal\u00f3n no rebota. En su lugar, puedes colocar el bal\u00f3n en una casilla desocupada adyacente a la casilla donde este jugador es derribado o aturdido (colocado boca abajo)."
                }
            },
            {
                "name": {
                    "en": "Diving Catch",
                    "es": "Recepci\u00f3n Heroica"
                },
                "family": "Agility",
                "description": {
                    "en": "The player is superb at diving to catch balls others cannot reach and jumping to more easily catch perfect passes. The player may add 1 to any catch roll from an accurate pass targeted to his square. In addition, the player can attempt to catch any pass, kick off or crowd throw-in, but not bouncing ball, that would land in an empty square in one of his tackle zones as if it had landed in his own square without leaving his current square. A failed catch will bounce from the Diving Catch player\u2019s square. If there are two or more players attempting to use this skill then they get in each other\u2019s way and neither can use it.",
                    "es": "(Diving Catch) El jugador puede intentar atrapar el bal\u00f3n si un pase, devoluci\u00f3n del campo o patada inicial cae en la zona de defensa de este jugador, esta habilidad no funciona si el bal\u00f3n entra en la zona de defensa rebotando. Adem\u00e1s, tiene un +1 a la tirada de Agilidad para atrapar un pase preciso en la propia casilla del jugador."
                }
            },
            {
                "name": {
                    "en": "Defensive",
                    "es": "Rompe defensas"
                },
                "family": "Agility",
                "description": {
                    "en": "During your opponent\u2019s team turn (but not during your own team), any opposition player being marked by this player cannot use the guard skill.",
                    "es": "S\u00f3lo durante el turno del oponente (No durante tu propio turno), cualquier jugador rival con la habilidad Defensa no puede usarla si esta en zona de defensa de este jugador."
                }
            },
            {
                "name": {
                    "en": "Leap",
                    "es": "Saltar"
                },
                "family": "Agility",
                "description": {
                    "en": "A player with the Leap skill is allowed to jump to any empty square within 2 squares even if it requires jumping over a player from either team. Making a leap costs the player two squares of movement. In order to make the leap, move the player to any empty square 1 to 2 squares from his current square and then make an Agility roll for the player. No modifiers apply to this D6 roll unless he has Very Long Legs. The player does not have to dodge to leave the square he starts in. If the player successfully makes the D6 roll then he makes a perfect jump and may carry on moving. If the player fails the Agility roll then he is Knocked Down in the square that he was leaping to, and the opposing coach makes an Armour roll to see if he was injured. A player may only use the Leap skill once per turn.",
                    "es": "Un jugador con esta habilidad puede elegir saltar sobre cualquier casilla adyacente a una casilla libre u ocupada por un jugador en pie o tumbado, siguiendo las reglas de brincar. Reduce en 1 el modificador para Brincar o Saltar hasta un m\u00ednimo de -1. Un jugador con la Habilidad Pogo Saltar\u00edn no puede aprender Saltar."
                }
            }
        ]
    },
    {
        "family": "Passing",
        "items": [
            {
                "name": {
                    "en": "Cannoneer",
                    "es": "Ca\u00f1onero"
                },
                "family": "Passing",
                "description": {
                    "en": "When this player performs a Long Pass action or a Long Bomb Pass action, you may apply an additional +1 modifier to the Passing Ability test.",
                    "es": "Cuando este jugador realiza un Pase Largo o Bomba Larga puede a\u00f1adir +1 a la tirada de Pase."
                }
            },
            {
                "name": {
                    "en": "Leader",
                    "es": "L\u00edder"
                },
                "family": "Passing",
                "description": {
                    "en": "A team which has one or more players with this Skill gains a single extra team re-roll, However, the Leader re-roll can only be used if there is at least one player with this Skill on the pitch (even if the player with this Skill is Prone, Stunned or has lost their Tackle Zone). If all players with this Skill are removed from play before the Leader re-roll is used, is lost. The Leader Re-roll can be carried over into extra time if it is not used, but the team does not receive a new one at the start of extra time. Unlike standard Team Re-rolls, the Leader Re-roll cannot be lost due to a Halfling Master Chef. Otherwise, the Leader re-roll is treated just like a normal team re-roll.",
                    "es": "Un equipo con un jugador con esta habilidad gana un Re-Roll de L\u00edder, s\u00f3lo puede usarse si un jugador con esta habilidad est\u00e1 en el campo, si el jugador sale del campo antes de haber usado esta Re-Roll, se pierde. Este Re-Roll puede usarse en la Pr\u00f3rroga si no se ha gastado. Esta Re-Roll no puede perderse con el Chef Halfling."
                }
            },
            {
                "name": {
                    "en": "Nerves of Steel",
                    "es": "Nervios de Acero"
                },
                "family": "Passing",
                "description": {
                    "en": "The player ignores modifiers for enemy tackle zones when he attempts to pass, catch or intercept.",
                    "es": "(Nerves of Steel) Este jugador puede ignorar los modificadores negativos por estar en zonas de defensa enemigas al Pasar, Atrapar o Interferir."
                }
            },
            {
                "name": {
                    "en": "Cloud Burster",
                    "es": "Parte Nubes"
                },
                "family": "Passing",
                "description": {
                    "en": "When this player performs a Long Pass action or a Long Bomb Pass action, you may choose to make the opposing coach re-roll a successful attempt to interfere with the pass.",
                    "es": "(Cloud Burster) Cuando este jugador realiza un Pase Largo o Bomba Larga, puedes obligar a repetir la tirada de Interferir el pase del rival."
                }
            },
            {
                "name": {
                    "en": "Pass",
                    "es": "Pasar"
                },
                "family": "Passing",
                "description": {
                    "en": "A player with the Pass skill is allowed to re-roll the D6 if he throws an inaccurate pass or fumbles.",
                    "es": "Este jugador puede repetir una tirada fallida de Pase cuando hace una Acci\u00f3n de Pase."
                }
            },
            {
                "name": {
                    "en": "Running Pass",
                    "es": "Pase en carrera"
                },
                "family": "Passing",
                "description": {
                    "en": "If this player performs a Quick Pass action, their activation does not have to end once the pass is resolved. If you wish and if this player has not used their full Movement Allowance, they may continue to move after resolving the pass.",
                    "es": "(Running Pass) Cuando este jugador realiza un Pase R\u00e1pido, puede continuar moviendo despu\u00e9s de efectuar el Pase."
                }
            },
            {
                "name": {
                    "en": "Hail Mary Pass",
                    "es": "Pase a lo Loco"
                },
                "family": "Passing",
                "description": {
                    "en": "The player may throw the ball to any square on the playing pitch, no matter what the range: the range ruler is not used. Roll a D6. On a roll of 1 the player fumbles the throw, and the ball will bounce once from the thrower\u2019s square. On a roll of 2-6, the player may make the pass. The Hail Mary pass may not be intercepted, but it is never accurate \u2013 the ball automatically misses and scatters three squares. Note that if you are lucky, the ball will scatter back into the target square! This skill may not be used in a Blizzard or with the Throw Team-Mate skill.",
                    "es": "(Hail Mary Pass) Cuando este jugador realice una acci\u00f3n de Pase (o Lanzar Bomba) puede elegir cualquier casilla del campo como objetivo. Independientemente del resultado de la tirada de PA, nunca ser\u00e1 un Pase Preciso, pero es necesario hacer la tirada para determinar si el pase es Bal\u00f3n Perdido o Muy Impreciso. Un Pase a lo Loco no puede Interferirse ni ser usado con Ventisca."
                }
            },
            {
                "name": {
                    "en": "Safe Pass",
                    "es": "Pase Seguro"
                },
                "family": "Passing",
                "description": {
                    "en": "Should This player fumble a Pass Action, the ball is not dropped, does not bounce from the square this player occupies, and no Turnover is caused. Instead, this player retains possession of the ball and their activation ends.",
                    "es": "(Safe Pass) Cuando este jugador obtiene un resultado de Bal\u00f3n Perdido en una acci\u00f3n de Pase, el bal\u00f3n no rebota y no causa cambio de turno, el bal\u00f3n se queda en posesi\u00f3n del Lanzador y acaba su acci\u00f3n inmediatamente."
                }
            },
            {
                "name": {
                    "en": "Accurate",
                    "es": "Precisi\u00f3n"
                },
                "family": "Passing",
                "description": {
                    "en": "The player may add 1 to the D6 roll when he passes.",
                    "es": "Cuando este jugador realiza un Pase R\u00e1pido o Pase Corto puede a\u00f1adir +1 a la tirada de Pase."
                }
            },
            {
                "name": {
                    "en": "Cannoneer",
                    "es": "Bombardero"
                },
                "family": "Passing",
                "description": {
                    "en": "When this player performs a Long Pass action or a Long Bomb Pass action, you may apply an additional +1 modifier to the Passing Ability test.",
                    "es": "Cuando se activa este jugador y est\u00e1 en pie, puede efectuar una acci\u00f3n especial de Lanzamiento de Bomba, esta acci\u00f3n No se considera ni Pase ni Lanzamiento de Compa\u00f1ero, pero s\u00f3lo se puede ejecutar un Lanzamiento de Bomba por turno. Una Bomba puede ser Lanzada, Atrapada e Interferida igual que un bal\u00f3n, usando las reglas habituales de Pase con las siguientes excepciones: \nUn jugador no puede levantarse o moverse antes de Lanzar una Bomba. La Bomba no rebota nunca, se mantiene en la casilla destinada. Si un jugador falla al atraparla, se mantendr\u00e1 en la casilla ocupada por el jugador. Si el Lanzamiento de Bomba es un Fumble, explotar\u00e1 inmediatamente en la casilla ocupada por el Lanzador. Si la Bomba cae en una casilla vac\u00eda o atrapada por un rival no causa cambio de turno. Un jugador en posesi\u00f3n del bal\u00f3n puede tambi\u00e9n coger una bomba. Cualquier habilidad usada para realizar un Pase (PA) puede usarse para Lanzar una Bomba, excepto En la Bola. Si la Bomba es atrapada por alg\u00fan jugador tira 1d6: \n4+, la Bomba explota como se describe a continuaci\u00f3n. 1-3, el jugador debe Lanzar la Bomba inmediatamente. Si la Bomba abandona el campo, explota en el p\u00fablico y se pierde. Cuando la Bomba cae en el suelo, sobre un jugador tumbado o en casilla ocupada por jugador y falla al atrapar, explota. \u2013 Si la Bomba explota en una casilla ocupada, el jugador es inmediatamente impactado. \u2013 Tira 1d6 por cada jugador adyacente a la casilla donde explota la Bomba. 4+, el jugador es impactado. 1-3, el jugador evita la explosi\u00f3n. Cualquier jugador en pie impactado por la Bomba, se tumba en el suelo. Se debe tirar por Armadura y Heridas si corresponde con un modificador de +1 a la Armadura o Heridas. Igualmente, para los jugadores tumbados impactados."
                }
            }
        ]
    },
    {
        "family": "Strength",
        "items": [
            {
                "name": {
                    "en": "Break Tackle",
                    "es": "Abrirse Paso"
                },
                "family": "Strength",
                "description": {
                    "en": "Once during their activation, after making an Agility test in order to Dodge, this player may modify the dice roll by +1 if their Strength characteristic is 4 or less, or by +2 if their Strength characteristic is 5 or more.",
                    "es": "(Break Tackle) Una vez por activaci\u00f3n, tras hacer un chequeo de agilidad para esquivar, este jugador modifica la tirada del dado en +1 si su atributo fuerza es de 4 o menos, o en +2 si su atributo fuerza es de 5 o m\u00e1s."
                }
            },
            {
                "name": {
                    "en": "Grab",
                    "es": "Apartar"
                },
                "family": "Strength",
                "description": {
                    "en": "A player with this skill uses his great strength and prowess to grab his opponent and throw him around. To represent this, only while making a Block Action, if his block results in a push back he may choose any empty square adjacent to his opponent to push back his opponent. When making a Block or Blitz Action, Grab and Side Step will cancel each other out and the standard pushback rules apply. Grab will not work if there are no empty adjacent squares. A player with the Grab skill can never learn or gain the Frenzy skill through any means. Likewise, a player with the Frenzy skill can never learn or gain the Grab skill through any means.",
                    "es": "Cuando este jugador realiza una acci\u00f3n de Placaje (en s\u00ed misma o como parte de una acci\u00f3n de penetraci\u00f3n), puede utilizar la habilidad de Apartar para impedir que el blanco del placaje utilice a su vez la habilidad de Echarse a un lado. Adem\u00e1s, cuando este jugador realice una acci\u00f3n de placaje (que no sea parte de una acci\u00f3n de penetraci\u00f3n), si el blanco resulta empujado puedes elegir cualquier casilla desocupada adyacente al blanco y empujarlo all\u00ed. Si no hay casillas desocupadas adyacentes al blanco, esta habilidad no puede utilizarse. Un jugador con esta habilidad no puede tener la habilidad de furia."
                }
            },
            {
                "name": {
                    "en": "Strong Arm",
                    "es": "Brazo Fuerte"
                },
                "family": "Strength",
                "description": {
                    "en": "This player may apply a +1 modifier to any Passing Ability test rolls they make when performing a Throw Team-mate action. A player that does not have the Throw team-mate trait cannot have this Skill.",
                    "es": "(Strong Arm) Este jugador puede aplicar un modificador de +1 a cualquier chequeo de pase que efectu\u00e9 al realizar una acci\u00f3n de Lanzar Compa\u00f1ero. Un jugador que no tenga el rasgo lanzar compa\u00f1ero no puede tener esta habilidad."
                }
            },
            {
                "name": {
                    "en": "Thick Skull",
                    "es": "Cabeza Dura"
                },
                "family": "Strength",
                "description": {
                    "en": "When an Injury roll is made against this player (even if this player is Prone, Stunned or has lost their Tackle Zone), they can only be KO\u2019d on a roll of 9, and will treat a roll of 8 as stunned result. If this player also has the Stunty trait, they can only be KO\u2019d on a roll of 8, and will treat a roll of 7 as Stunned result. All other results are unaffected.",
                    "es": "(Thick Skull) Cuando se haga una tirada de heridas contra este jugador ( incluso si esta tumbado boca arriba, aturdido o ha perdido su zona de defensa), solo quedara Inconsciente con un resultado de 9, y tratara el resultado de 8 como Aturdido. En cambio, si este jugador tienes adem\u00e1s el rasgo Escurridizo, solo quedara inconsciente con un resultado de 8, y tratara el resultado de 7 como aturdido. Los dem\u00e1s resultados de la tabla de heridas no se ven afectados por la habilidad Cabeza Dura."
                }
            },
            {
                "name": {
                    "en": "Pile Driver",
                    "es": "Crujir"
                },
                "family": "Strength",
                "description": {
                    "en": "When an opposition player is Knocked Down by this player as the result of a Block action (on its own or as part of a Blitz action), this player may immediately commit a free Foul action against the Knocked Down player. To use this Skill, this player must be Standing after the block dice result has been selected and applied, and must occupy a square adjacent to the Knocked Down player, After using this Skill, this player is Placed Prone and their activation ends immediately.",
                    "es": "(Pile Driver) Cuando un jugador rival sea Derribado por este jugador debido a una acci\u00f3n de Placaje (sea o no parte de una acci\u00f3n de penetraci\u00f3n), este jugador puede cometer de inmediato una acci\u00f3n de falta gratuita contra el jugador al que acaba de derribar. Para poder utilizar esta habilidad, este jugador debe estar en pie tras elegir y aplicar el resultado de los dados de placajes, y adem\u00e1s debe ocupar una casilla adyacente al jugador rival derribado. Tras utilizar esta habilidad, este jugador se coloca Tumbado boca arriba y su activaci\u00f3n finaliza inmediatamente."
                }
            },
            {
                "name": {
                    "en": "Guard",
                    "es": "Defensa"
                },
                "family": "Strength",
                "description": {
                    "en": "A player with this skill assists an offensive or defensive block even if he is in another player\u2019s tackle zone. This skill may not be used to assist a foul.",
                    "es": "Cuando un jugador realiza una Acci\u00f3n de Placaje (incluyendo como parte de una Acci\u00f3n de Blitz) este jugador puede ofrecer asistencias tanto ofensivas como defensivas independientemente de cu\u00e1ntos jugadores rivales los est\u00e9n Marcando."
                }
            },
            {
                "name": {
                    "en": "Mighty Blow",
                    "es": "Golpe Mort\u00edfero"
                },
                "family": "Strength",
                "description": {
                    "en": "Add 1 to any Armour or Injury roll made by a player with this skill when an opponent is Knocked Down by this player during a block. Note that you only modify one of the dice rolls, so if you decide to use Mighty Blow to modify the Armour roll, you may not modify the Injury roll as well. Mighty Blow cannot be used with the Stab or Chainsaw skills.",
                    "es": "(Mighty Blow) Cuando este jugador realiza una acci\u00f3n de Placaje (sea o no parte de una acci\u00f3n de penetraci\u00f3n) que tiene como resultado que un jugador rival sea derribado, puedes modificar o bien la tirada de armadura o bien la tirada de heridas en una cantidad igual al numero indicado entre par\u00e9ntesis. Esta habilidad no puede utilizarse en combinaci\u00f3n con los rasgos apu\u00f1alar o motosierra."
                }
            },
            {
                "name": {
                    "en": "Juggernaut",
                    "es": "Imparable"
                },
                "family": "Strength",
                "description": {
                    "en": "A player with this skill is virtually impossible to stop once he is in motion. If this player takes a Blitz Action, the opposing player may not use his Fend, Stand Firm or Wrestle skills against the Juggernaut player\u2019s blocks. The Juggernaut player may also choose to treat a !Both Down\u2019 result as if a !Pushed\u2019 result has been rolled instead for blocks he makes during a Blitz Action.",
                    "es": "Cuando este jugador realiza un placaje como parte de una acci\u00f3n de penetraci\u00f3n (pero no una acci\u00f3n de Placaje en s\u00ed misma), puedes elegir tratar un resultado de Ambos jugadores derribados como resultado de Empuj\u00f3n. Adem\u00e1s, cuando este jugador realiza una acci\u00f3n de placaje como parte de acci\u00f3n de penetraci\u00f3n, el blanco de dicho placaje no puede usar habilidades de Forcejeo, Mantenerse firme ni Zafarse."
                }
            },
            {
                "name": {
                    "en": "Arm Bar",
                    "es": "Llave de Brazo"
                },
                "family": "Strength",
                "description": {
                    "en": "If an opposition player Falls Over as a result of failing their Agility test when attempting to Dodge, Jump or Leap out of a square in which they were being Marked by this player, you may apply a +1 modifier to either the armour roll or Injury roll. This modifier may be applied after the roll has been made and may be applied even if this player is row Prone. If the opposition player was being marked by more than one player with this Skill, only one player may use it.",
                    "es": "(Arm Bar) Si un jugador rival cae por haber fallado su chequeo de agilidad al intentar Esquivar, Saltar o Brincar para salir de una casilla en la que esta siendo marcado por este jugador, puede aplicar un modificador de +1 o bien a la tirada de armadura o bien a la tirada de herida. Este modificador puede aplicarse tras hacer la tirada en cuesti\u00f3n y puede aplicarse incluso si este jugador est\u00e1 ahora tumbado boca abajo. Si el jugador rival esta siendo marcado a la vez por varios jugadores con esta habilidad, solo uno de ellos podr\u00e1 utilizarla."
                }
            },
            {
                "name": {
                    "en": "Brawler",
                    "es": "Luchador"
                },
                "family": "Strength",
                "description": {
                    "en": "When this player performs a Block action on its own (but not as part of a Blitz Action), this player may re-roll a single Both Down result.",
                    "es": "Cuando este jugador realiza una acci\u00f3n de Placaje (que NO sea parte de un Blitz), puede repetir un \u00fanico dado con resultado de ambos jugadores derribados."
                }
            },
            {
                "name": {
                    "en": "Stand Firm",
                    "es": "Mantenerse Firme"
                },
                "family": "Strength",
                "description": {
                    "en": "This player may choose not to be pushed back, either as the result of a Block action made against them or by a chain-push. Using this Skill does not prevent an opposition player with the Frenzy Skill from performing a second Block action if this player is still Standing after the first.",
                    "es": "(Stand Firm) Este jugador puede elegir no ser empujado, ya sea como resultado de una acci\u00f3n de placaje contra \u00e9l o debido a un empuj\u00f3n en cadena. El uso de\u00a0 esta habilidad no impide a un jugador rival con la habilidad furia realizar una segunda acci\u00f3n de placaje contra este jugador, si este jugador sigue en pie tras el primer placaje."
                }
            },
            {
                "name": {
                    "en": "Multiple Block",
                    "es": "Placaje M\u00faltiple"
                },
                "family": "Strength",
                "description": {
                    "en": "At the start of a Block Action a player who is adjacent to at least two opponents may choose to throw blocks against two of them. Make each block in turn as normal except that each defender\u2019s strength is increased by 2. The player cannot follow up either block when using this skill, so Multiple Block can be used instead of Frenzy, but both skills cannot be used together. To have the option to throw the second block the player must still be on his feet after the first block.",
                    "es": "(Multiple Block) Cuando este jugador realiza una acci\u00f3n de Placaje (que no sea parte de una acci\u00f3n de penetraci\u00f3n), puede elegir efectuar dos acciones de Placaje, cada una de ellas tomando como blanco a un jugador rival distinto al que este marcando. No obstante, al hacer esto el atributo fuerza de este jugador se reduce en 2 durante el resto de esa activaci\u00f3n. Ambas acciones de placaje se efect\u00faan de manera simult\u00e1nea, lo que quiere decir que se resuelve por completo incluso aunque una de ellas (o las dos) provoque un cambio de turno. A fin de evitar confusiones, las tiradas para cada acci\u00f3n de Placaje deber\u00edan mantenerse separadas. Este jugador no puede hacer movimientos de impulso al utilizar esta habilidad. Ten en cuenta que elegir utilizar esta habilidad significa que este jugador no podr\u00e1 utilizar la habilidad Furia durante la misma activaci\u00f3n."
                }
            }
        ]
    },
    {
        "family": "Mutation",
        "items": [
            {
                "name": {
                    "en": "Foul Appearance",
                    "es": "Apariencia Asquerosa"
                },
                "family": "Mutation",
                "description": {
                    "en": "When an opposition player declares a Block action targeting this player (on its own or as part of a Blitz action), or any Special actions that targets this player, their coach must firs roll a D6, even if this player has lost their Tackle Zone. On a roll of 1, the player cannot perform the declared action and the action is wasted.\u00a0This Skill may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                    "es": "(Foul Appearance) Cuando un jugador contrario declara una acci\u00f3n de Placaje dirigida a este jugador (por s\u00ed sola o como parte de una acci\u00f3n Blitz), o cualquier acci\u00f3n Especial dirigida a este jugador, su entrenador debe tirar primero un dado D6, incluso si este jugador ha perdido su Zona de Defensa. Con una tirada de 1, el jugador no puede realizar la acci\u00f3n declarada y la acci\u00f3n se desperdicia. Esta habilidad puede seguir us\u00e1ndose si el jugador est\u00e1 tumbado o ha perdido su Zona de Defensa."
                }
            },
            {
                "name": {
                    "en": "Extra Arms",
                    "es": "Brazos Adicionales"
                },
                "family": "Mutation",
                "description": {
                    "en": "A player with one or more extra arms may add 1 to any attempt to pick up, catch or intercept.",
                    "es": "(Extra Arms) Este jugador puede aplicar +1 cuando intenta coger el bal\u00f3n del suelo, Atrapar Bal\u00f3n o Interferir un pase."
                }
            },
            {
                "name": {
                    "en": "Prehensile Tail",
                    "es": "Cola Prensil"
                },
                "family": "Mutation",
                "description": {
                    "en": "When an active opposition player attempts to Dodge, Jump or Leap in order to vacate a square in which they are being Marked by this player, there is an additional -1 modifier applied to the active player\u2019s Agility test. If the opposition player is being Marked by more than one player with this Mutation, only one player may use it.",
                    "es": "(Prehensile Tail) Cuando un jugador rival intenta esquivar, saltar o brincar para abandonar una casilla en la que est\u00e1 siendo marcado por este jugador, se aplica un modificador adicional de -1 a la prueba de Agilidad del jugador activo. Si el jugador contrario est\u00e1 siendo marcado por m\u00e1s de un jugador con esta Mutacion, s\u00f3lo un jugador puede usarla."
                }
            },
            {
                "name": {
                    "en": "Horns",
                    "es": "Cuernos"
                },
                "family": "Mutation",
                "description": {
                    "en": "A player with Horns may use them to butt an opponent. Horns adds 1 to the player\u2019s Strength for any block(s) he makes during a Blitz Action.",
                    "es": "Cuando el jugador realiza una acci\u00f3n de Placaje como parte de una acci\u00f3n Blitz (pero no por s\u00ed sola), puedes aplicar un modificador +1 a la caracter\u00edstica de Fuerza de este jugador. Este modificador se aplica antes de contar las asistencias, antes de aplicar cualquier otro modificador de Fuerza y antes de usar cualquier otra Habilidad o Rasgo."
                }
            },
            {
                "name": {
                    "en": "Two Heads",
                    "es": "Dos Cabezas"
                },
                "family": "Mutation",
                "description": {
                    "en": "This player may apply a +1 modifier to the Agility test when they attempt to Dodge.",
                    "es": "(Two Heads) Este jugador puede aplicar un +1 a la tirada de Agilidad cuando hace una Esquiva."
                }
            },
            {
                "name": {
                    "en": "Claws",
                    "es": "Garras"
                },
                "family": "Mutation",
                "description": {
                    "en": "A player with this skill is blessed with a huge crab-like claw or razor sharp talons that make armour useless. When an opponent is Knocked Down by this player during a block, any Armour roll of 8 or more after modifications automatically breaks armour.",
                    "es": "Cuando hagas una tirada de Armadura contra un rival que haya sido derribado como resultado de una acci\u00f3n de Placaje o Blitz hecha por este jugador, con 8+ antes de aplicar modificadores superar\u00e1 la tirada de Armadura."
                }
            },
            {
                "name": {
                    "en": "Big Hand",
                    "es": "Mano Grande"
                },
                "family": "Mutation",
                "description": {
                    "en": "One of the player\u2019s hands has grown monstrously large, yet remained completely functional. The player ignores modifier(s) for enemy tackle zones or Pouring Rain weather when he attempts to pick up the ball.",
                    "es": "(Big Hand) Este jugador puede ignorar los modificadores negativos por zonas de defensa o por las condiciones clim\u00e1ticas de lluvia torrencial al intentar coger el bal\u00f3n del suelo."
                }
            },
            {
                "name": {
                    "en": "Very Long Legs",
                    "es": "Piernas Muy Largas"
                },
                "family": "Mutation",
                "description": {
                    "en": "This player may reduce any negative modifier applied to the Agility test when they attempt to Jump over a Prone or Stunned player (or to Leap over an empty square or a square occupied by a Standing player, if this player has the Leap Skill) by 1, to a minimum of -1. Additionally, this player may apply a +2 modifier to any attempts to interfere with a pass they make. Finally this player ignores the Cloud Burster skill.",
                    "es": "(Very Long Legs) Este jugador puede reducir en 1 cualquier modificador negativo aplicado a la prueba de Agilidad cuando intente saltar sobre un jugador Tumbado boca arriba o Aturdido (o saltar sobre una casilla vac\u00eda o una casilla ocupada por un jugador de pie, si este jugador tiene la habilidad Saltar), hasta un m\u00ednimo de -1. Adem\u00e1s, este jugador puede aplicar un modificador de +2 a cualquier intento de interferir en un pase que realice. Por \u00faltimo, este jugador ignora la habilidad Parte Nubes."
                }
            },
            {
                "name": {
                    "en": "Disturbing Presence",
                    "es": "Presencia Perturbadora"
                },
                "family": "Mutation",
                "description": {
                    "en": "This player\u2019s presence is very disturbing, whether it is caused by a massive cloud of flies, sprays of soporific musk, an aura of random chaos or intense cold, or a pheromone that causes fear and panic. Regardless of the nature of this mutation, any player must subtract 1 from the D6 when they pass, intercept or catch for each opposing player with Disturbing Presence that is within three squares of them, even if the Disturbing Presence player is Prone or Stunned.",
                    "es": "(Disturbing Presence) Cuando un oponente intente hacer una acci\u00f3n de Pase, Lanzar Compa\u00f1ero, Lanzar Bomba, Interferir Pase o Atrapar bal\u00f3n debe aplicar un -1 por cada jugador con esta habilidad que se encuentra a 3 casillas o menos. Incluso si est\u00e1 Tumbado en el suelo o ha perdido su Zona de Defensa."
                }
            },
            {
                "name": {
                    "en": "Tentacles",
                    "es": "Tent\u00e1culos"
                },
                "family": "Mutation",
                "description": {
                    "en": "This player can use this Skill when an opposition player they are Marking voluntarily moves out of a square within this player\u2019s Tackle Zone. Roll a D6, adding the ST of this player to the roll and then subtracting the ST of the opposition player. If the result is 6 or higher, or if the roll is a natural 6, the opposition player is held firmly in place and their movement comes to an end. If, however, the result is 5 or lower, or if the roll is a natural 1, this Skill has no further effect. A player may use this Skill any number or times per turn, during either team\u2019s turn. If an opposition player is being Marked by more than one player with this Skill, only one player may use it.",
                    "es": "Este jugador puede usar esta habilidad cuando un jugador contrario al que est\u00e1 marcando se desplaza voluntariamente fuera de una casilla dentro de su zona de placaje. Tira un D6, sumando la Fuerza de este jugador a la tirada y restando la Fuerza del jugador contrario. Si el resultado es 6 o m\u00e1s, o si la tirada es un 6 natural, el jugador adversario es retenido firmemente en su sitio y su movimiento finaliza. Sin embargo, si el resultado es 5 o inferior, o si la tirada es un 1 natural, esta Habilidad no tiene ning\u00fan efecto. Un jugador puede usar esta Habilidad cualquier n\u00famero de veces por turno, durante el turno de cualquiera de los dos equipos. Si un jugador contrario est\u00e1 siendo marcado por m\u00e1s de un jugador con esta habilidad, s\u00f3lo un jugador puede usarla."
                }
            },
            {
                "name": {
                    "en": "Monstrous Mouth",
                    "es": "Boca Monstruosa"
                },
                "family": "Mutations",
                "description": {
                    "en": "This player may re-roll any failed attempt to catch the ball. In addition, the Strip Ball skill cannot be used against this player.",
                    "es": "(Monstrous Mouth) El jugador puede repetir cualquier intento de Atrapar el bal\u00f3n, adem\u00e1s no se puede usar Robar Bal\u00f3n contra este jugador."
                }
            },
            {
                "name": {
                    "en": "Iron Hard Skin",
                    "es": "Piel Ferrea"
                },
                "family": "Mutations",
                "description": {
                    "en": "The Claws skill cannot be used when making an armour roll against this player.\u00a0This Skill may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                    "es": "(Iron Hard Skin) La habilidad Garras no puede usarse al hacer una tirada de armadura contra este jugador. Esta habilidad a\u00fan puede usarse si el jugador est\u00e1 Tumbado, Aturdido, o ha perdido su Zona de Defensa."
                }
            }
        ]
    }
]);
