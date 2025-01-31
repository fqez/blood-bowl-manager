let now = new Date();
db['perks'].insertMany(
    [
        {
            "id": "perk-dauntless",
            "name": {
                "en": "Dauntless",
                "es": "Agallas"
            },
            "family": "General",
            "description": {
                "en": "A player with this skill is capable of psyching himself up so he can take on even the very strongest opponent. The skill only works when the player attempts to block an opponent who is stronger than himself. When the skill is used, the coach of the player with the Dauntless skill rolls a D6 and adds it to his strength. If the total is equal to or lower than the opponent’s Strength, the player must block using his normal Strength. If the total is greater, then the player with the Dauntless skill counts as having a Strength equal to his opponent’s when he makes the block. The strength of both players is calculated before any defensive or offensive assists are added but after all other modifiers.",
                "es": "Cuando el jugador realiza una acción de Placaje, incluido el Blitz, si el rival objetivo tiene más Fuerza que el jugador antes de aplicar modificadores por apoyos, tira 1d6 y añade la Fuerza del jugador, si el total es superior a la Fuerza del rival objetivo, el jugador aumenta su Fuerza hasta igualar la del rival durante este Placaje, después deben aplicarse los apoyos. En caso de que el jugador tenga la habilidad como Furia, que le permite hacer dos Placajes, debe tirar Agallas por cada uno de ellos."
            }
        },
        {
            "id": "perk-drunkard",
            "name": {
                "en": "Drunkard",
                "es": "Borracho"
            },
            "family": "Extraordinary",
            "description": {
                "en": "This player suffers a -1 penality to the dice roll when attempting to Rush.",
                "es": "Este jugador sufre una penalización de -1 a la tirada de dados cuando intenta precipitarse. (A Por Ellos)"
            }
        },
        {
            "id": "perk-wrestle",
            "name": {
                "en": "Wrestle",
                "es": "Forcejeo"
            },
            "family": "General",
            "description": {
                "en": "The player is specially trained in grappling techniques. This player may use Wrestle when he blocks or is blocked and a !Both Down’ result on the Block dice is chosen by either coach. Instead of applying the ‘Both Down’ result, both players are wrestled to the ground. Both players are Placed Prone in their respective squares even if one or both have the Block skill. Do not make Armour rolls for either player. Use of this skill does not cause a turnover unless the active player was holding the ball.",
                "es": "Este jugador puede usar esta habilidad con el resultado de «Ambos Derribados», en lugar de aplicarlo normalmente, ambos jugadores se tumban en el suelo boca arriba, sin necesidad de tirar Armadura. No causa cambio de turno."
            }
        },
        {
            "id": "perk-frenzy",
            "name": {
                "en": "Frenzy",
                "es": "Furia"
            },
            "family": "General",
            "description": {
                "en": "A player with this skill is a slavering psychopath who attacks his opponents in an uncontrollable rage. Unless otherwise overridden, this skill must always be used. When making a block, a player with this skill must always follow up if he can. If a ‘Pushed’ or ‘Defender Stumbles’ result was chosen, the player must immediately throw a second block against the same opponent so long as they are both still standing and adjacent. If possible, the player must also follow up this second block. If the frenzied player is performing a Blitz Action then he must pay a square of Movement and must make the second block unless he has no further normal movement and cannot Go For It again.",
                "es": "Cada vez que este jugador realice una acción de Placaje (sola o como parte de una acción Blitz), debe realizar un seguimiento si el objetivo es empujado hacia atrás y si puede hacerlo. Si el objetivo sigue en pie después de ser empujado hacia atrás, y si este jugador fue capaz de realizar el seguimiento, este jugador debe entonces realizar una segunda acción de Placaje contra el mismo objetivo, de nuevo ocupando a casilla del objetivo empujado hacia atrás. Si este jugador realiza una acción Blitz, realizar una segunda acción de Placaje también le costará uno de Movimiento. Si a este jugador no le queda Movimiento para realizar una segunda acción de Placaje, deberá Precipitarse para hacerlo. Si no puede correr, no puede realizar una segunda acción de Placaje. Ten en cuenta que si un jugador contrario en posesión del balón es empujado hacia tu Zona de Touch Down y sigue en pie, se marcará un touchdown, finalizando la entrada. En este caso, la segunda acción de Placaje no se realiza. Un jugador con esta habilidad no puede tener también la habilidad Apartar."
            }
        },
        {
            "id": "perk-dirty-player",
            "name": {
                "en": "Dirty Player",
                "es": "Jugar Sucio"
            },
            "family": "General",
            "description": {
                "en": "A player with this skill has trained long and hard to learn every dirty trick in the book. Add 1 to any Armour roll or Injury roll made by a player with this skill when they make a Foul as part of a Foul Action. Note that you may only modify one of the dice rolls, so if you decide to use Dirty Player to modify the Armour roll, you may not modify the Injury roll as well.",
                "es": "(Dirty Player) Cuando este jugador comete una Falta, puede añadir (+X) a la tirada de Armadura o Heridas."
            }
        },
        {
            "id": "perk-sure-hands",
            "name": {
                "en": "Sure Hands",
                "es": "Manos Seguras"
            },
            "family": "General",
            "description": {
                "en": "A player with the Sure Hands skill is allowed to re-roll the D6 if he fails to pick up the ball. In addition, the Strip Ball skill will not work against a player with this skill.",
                "es": "(Sure Hands) El jugador puede repetir una tirada fallida de AG al intentar recoger el balón del suelo. Además, el rival no puede usar Robar Balón."
            }
        },
        {
            "id": "perk-kick",
            "name": {
                "en": "Kick",
                "es": "Patada"
            },
            "family": "General",
            "description": {
                "en": "The player is an expert at kicking the ball and can place the kick with great precision. In order to use this skill the player must be set up on the pitch when his team kicks off. The player may not be set up in either wide zone or on the line of scrimmage. Only if all these conditions are met is the player then allowed to take the kick-off. Because his kick is so accurate, you may choose to halve the number of squares that the ball scatters on kick-off, rounding any fractions down (i.e., 1 = 0, 2-3 = 1, 4- 5 = 2, 6 = 3).",
                "es": "Si este jugador es elegido como el jugador que da la Patada Inicial, puede elegir reducir a la mitad el número de casillas que se desvía el balón, redondeando hacia abajo."
            }
        },
        {
            "id": "perk-shadowing",
            "name": {
                "en": "Shadowing",
                "es": "Perseguir"
            },
            "family": "General",
            "description": {
                "en": "The player may use this skill when a player performing an Action on the opposing team moves out of any of his tackle zones for any reason. The opposing coach rolls 2D6 adding his own player’s movement allowance and subtracting the Shadowing player’s movement allowance from the score. If the final result is 7 or less, the player with Shadowing may move into the square vacated by the opposing player. He does not have to make any Dodge rolls when he makes this move, and it has no effect on his own movement in his own turn. If the final result is 8 or more, the opposing player successfully avoids the Shadowing player and the Shadowing player may not move into the vacated square. A player may make any number of shadowing moves per turn. If a player has left the tackle zone of several players that have the Shadowing skill, then only one of the opposing players may attempt to shadow him.",
                "es": "Este jugador puede usar esta habilidad cuando un oponente abandona voluntariamente su zona de defensa. Tira 1d6 y suma el MO del jugador, restando el MO del rival, si la diferencia es 6+, el jugador puede ocupar inmediatamente la casilla abandonada por el rival, sin necesidad de hacer tirada de esquivar alguna. El jugador puede usar esta habilidad múltiples veces por turno, pero sólo un jugador puede usarla si hay varios con posibilidad de hacerlo."
            }
        },
        {
            "id": "perk-tackle",
            "name": {
                "en": "Tackle",
                "es": "Placaje Defensivo"
            },
            "family": "General",
            "description": {
                "en": "Opposing players who are standing in any of this player’s tackle zones are not allowed to use their Dodge skill if they attempt to dodge out of any of the player’s tackle zones, nor may they use their Dodge skill if the player throws a block at them and uses the Tackle skill.",
                "es": "Cuando un jugador rival intenta esquivar desde la zona de defensa de este jugador, el rival no puede usar su habilidad Esquivar. Además, cuando un rival es objetivo de un Placaje, o Blitz tampoco puede usarla."
            }
        },
        {
            "id": "perk-block",
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
            "id": "perk-pro",
            "name": {
                "en": "Pro",
                "es": "Profesional"
            },
            "family": "General",
            "description": {
                "en": "A player with this skill is a hardened veteran. Such players are called professionals or Pros by other Blood Bowl players because they rarely make a mistake. Once per turn, a Pro is allowed to re-roll any one dice roll he has made other than Armour, Injury or Casualty, even if he is Prone or Stunned. However, before the re-roll may be made, his coach must roll a D6. On a roll of 4, 5 or 6 the re-roll may be made. On a roll of 1, 2 or 3 the original result stands and may not be re-rolled with a skill or team re-roll; however you can re-roll the Pro roll with a Team re-roll.",
                "es": "Durante su activación este jugador puede intentar Repetir un único dado, incluso si forma parte de un grupo de dados, excepto tiradas de Armadura, Heridas o lesiones. Tira un D6: – 3+, el dado elegido puede ser repetido. – 1-2, el dado no se puede repetir. Una vez usada esta habilidad, ya no se puede usar Re-Roll para esta tirada."
            }
        },
        {
            "id": "perk-strip-ball",
            "name": {
                "en": "Strip Ball",
                "es": "Robar Balón"
            },
            "family": "General",
            "description": {
                "en": "When a player with this skill blocks an opponent with the ball, applying a !Pushed’ or !Defender Stumbles’ result will cause the opposing player to drop the ball in the square that they are pushed to, even if the opposing player is not Knocked Down.",
                "es": "(Strip Ball) Cuando este jugador elige como objetivo a un rival en posesión del balón como acción de Placaje o Blitz, puede obligar a soltar el balón en caso de obtener un resultado de empujón. El balón rebotará desde la casilla en la que se empuja al rival como si fuese tumbado."
            }
        },
        {
            "id": "perk-fend",
            "name": {
                "en": "Fend",
                "es": "Zafarse"
            },
            "family": "General",
            "description": {
                "en": "This player is very skilled at holding off would-be attackers. Opposing players may not follow-up blocks made against this player even if the Fend player is Knocked Down. The opposing player may still continue moving after blocking if he had declared a Blitz Action.",
                "es": "Si este jugador es empujado hacia atrás como consecuencia de cualquier resultado de dados de Placaje que se aplique contra él, puede elegir impedir que el jugador que le empujó hacia atrás le siga. Sin embargo, el jugador que le hizo retroceder puede continuar moviéndose como parte de una acción Blitz si le queda Movimiento. La habilidad no puede usarse cuando este jugador es empujado en cadena, contra un jugador con el rasgo de Bola y Cadena o contra un jugador con la habilidad Imparable que realizó la acción de Placaje como parte de un Blitz."
            }
        },
        {
            "id": "perk-catch",
            "name": {
                "en": "Catch",
                "es": "Atrapar"
            },
            "family": "Agility",
            "description": {
                "en": "A player who has the Catch skill is allowed to re-roll the D6 if he fails a catch roll. It also allows the player to re-roll the D6 if he drops a hand-off or fails to make an interception.",
                "es": "El jugador puede repetir una tirada fallida de AG al intentar atrapar un balón."
            }
        },
        {
            "id": "perk-jump-up",
            "name": {
                "en": "Jump Up",
                "es": "En Pie de un Salto"
            },
            "family": "Agility",
            "description": {
                "en": "A player with this skill is able to quickly get back into the game. If the player declares any Action other than a Block Action he may stand up for free without paying the three squares of movement. The player may also declare a Block Action while Prone which requires an Agility roll with a +2 modifier to see if he can complete the Action. A successful roll means the player can stand up for free and block an adjacent opponent. A failed roll means the Block Action is wasted and the player may not stand up.",
                "es": "(Jump Up) Si este jugador está en el suelo, puede levantarse sin gastar ningún punto de Movimiento, además puede intentar hacer acción de Placaje desde el suelo (Sin gastar la acción de Blitz), debe superar una tirada de Agilidad con +1, si tiene éxito, el jugador se levanta y hace el Placaje normalmente, si no se queda tumbado en el suelo y pierde su acción. Esta Habilidad puede seguir usándose si el jugador está Tumbado o ha perdido su Zona de defensa."
            }
        },
        {
            "id": "perk-sprint",
            "name": {
                "en": "Sprint",
                "es": "Esprintar"
            },
            "family": "Agility",
            "description": {
                "en": "When this player performs any action that includes movement, they may attempt to Rush three times, rather than the usual two.",
                "es": "Cuando este jugador realiza cualquier acción que incluye moverse, puede intentar Forzar la marcha hasta tres veces, en lugar de las dos habituales."
            }
        },
        {
            "id": "perk-dodge",
            "name": {
                "en": "Dodge",
                "es": "Esquivar"
            },
            "family": "Agility",
            "description": {
                "en": "A player with the Dodge skill is adept at slipping away from opponents, and is allowed to re-roll the D6 if he fails to dodge out of any of an opposing player’s tackle zones. However, the player may only re-roll one failed Dodge roll per turn. In addition, the Dodge skill, if used, affects the results rolled on the Block dice, as explained in the Blocking rules.",
                "es": "Una vez por turno de equipo, durante su activación, este jugador puede repetir un chequeo de Agilidad fallido para intentar esquivar. Además, este jugador puede usar su habilidad esquivar cuando sea blanco de una acción de Placaje (por si solo o como parte de un Blitz ) y se obtenga un resultado de «Desequilibrio» contra el."
            }
        },
        {
            "id": "perk-sneaky-git",
            "name": {
                "en": "Sneaky Git",
                "es": "Furtivo"
            },
            "family": "Agility",
            "description": {
                "en": "During a Foul Action a player with this skill is not ejected for rolling natural doubles on the Armour roll.",
                "es": "(Sneaky Git) Cuando este jugador realiza una acción de falta, no es expulsado por sacar un doble natural en la tirada de armadura. Aun asi, podra ser expulsado si saca un doble natural en la tirada de herida."
            }
        },
        {
            "id": "perk-hit-and-run",
            "name": {
                "en": "Hit and Run",
                "es": "Golpear y correr"
            },
            "family": "Extraordinary",
            "description": {
                "en": "After a player with this Trait performs a Block action, they may immediately move one free square ignoring Tackle Zones so long as they are still Standing. They must ensure that after this free move, they are not Marked by or Marking any opposition players.",
                "es": "(Hit and Run) Después de que un jugador con este rasgo realice una acción de Placar, puede moverse inmediatamente en una casilla libre ignorando las zonas de placaje mientras siga en pie. Deben asegurarse de que, tras este movimiento libre, no son marcados por ningún jugador rival."
            }
        },
        {
            "id": "perk-sure-feet",
            "name": {
                "en": "Sure Feet",
                "es": "Pies Firmes"
            },
            "family": "Agility",
            "description": {
                "en": "Once per team turn, during their activation, this player may re-roll the D6 when attempting to Rush.",
                "es": "(Sure Feet) Una vez por turno de equipo, durante la activación de este jugador, este jugador puede repetir la tirada al intentar Forzar la marcha."
            }
        },
        {
            "id": "perk-diving-tackle",
            "name": {
                "en": "Diving Tackle",
                "es": "Placaje Heroico"
            },
            "family": "Agility",
            "description": {
                "en": "The player may use this skill after an opposing player attempts to dodge out of any of his tackle zones. The opposing player must subtract 2 from his Dodge roll for leaving the player’s tackle zone. If a player is attempting to leave the tackle zone of several players that have the Diving Tackle skill, then only one of the opposing players may use Diving Tackle. Diving Tackle may be used on a re-rolled dodge if not declared for use on the first Dodge roll. Once the dodge is resolved but before any armour roll for the opponent (if needed), the Diving Tackle Player is Placed Prone in the square vacated by the dodging player but do not make an Armour or Injury roll for the Diving Tackle player.",
                "es": "(Diving Tackle) Cuando un oponente obtiene un éxito en la tirada de Agilidad y abandona la zona de defensa del jugador al Esquivar, Saltar o Brincar, el jugador puede restar 2 a dicha tirada de Agilidad, este jugador se tumba en el suelo en la casilla abandonada, sin necesidad de tirada de Armadura. Sólo un jugador puede usar esta habilidad si hay varios con opción de hacerlo."
            }
        },
        {
            "id": "perk-safe-pair-of-hands",
            "name": {
                "en": "Safe Pair of Hands",
                "es": "Proteger el Cuero"
            },
            "family": "Agility",
            "description": {
                "en": "If this player is Knocked Down or Placed Prone (but not it they Fall Over) whilst in possession of the ball, the ball does not bounce. Instead, you may place the ball in an unoccupied square adjacent to the one this player occupies when they become Prone. This Skill may still be used if the player is Prone.",
                "es": "(Safe Pair of Hands) Si este jugador es derribado o colocado boca abajo (pero no si se cae) mientras está en posesión del balón, el balón no rebota. En su lugar, puedes colocar el balón en una casilla desocupada adyacente a la casilla donde este jugador es derribado o aturdido (colocado boca abajo)."
            }
        },
        {
            "id": "perk-diving-catch",
            "name": {
                "en": "Diving Catch",
                "es": "Recepción Heroica"
            },
            "family": "Agility",
            "description": {
                "en": "The player is superb at diving to catch balls others cannot reach and jumping to more easily catch perfect passes. The player may add 1 to any catch roll from an accurate pass targeted to his square. In addition, the player can attempt to catch any pass, kick off or crowd throw-in, but not bouncing ball, that would land in an empty square in one of his tackle zones as if it had landed in his own square without leaving his current square. A failed catch will bounce from the Diving Catch player’s square. If there are two or more players attempting to use this skill then they get in each other’s way and neither can use it.",
                "es": "(Diving Catch) El jugador puede intentar atrapar el balón si un pase, devolución del campo o patada inicial cae en la zona de defensa de este jugador, esta habilidad no funciona si el balón entra en la zona de defensa rebotando. Además, tiene un +1 a la tirada de Agilidad para atrapar un pase preciso en la propia casilla del jugador."
            }
        },
        {
            "id": "perk-defensive",
            "name": {
                "en": "Defensive",
                "es": "Rompe defensas"
            },
            "family": "Agility",
            "description": {
                "en": "During your opponent’s team turn (but not during your own team), any opposition player being marked by this player cannot use the guard skill.",
                "es": "Sólo durante el turno del oponente (No durante tu propio turno), cualquier jugador rival con la habilidad Defensa no puede usarla si esta en zona de defensa de este jugador."
            }
        },
        {
            "id": "perk-leap",
            "name": {
                "en": "Leap",
                "es": "Saltar"
            },
            "family": "Agility",
            "description": {
                "en": "A player with the Leap skill is allowed to jump to any empty square within 2 squares even if it requires jumping over a player from either team. Making a leap costs the player two squares of movement. In order to make the leap, move the player to any empty square 1 to 2 squares from his current square and then make an Agility roll for the player. No modifiers apply to this D6 roll unless he has Very Long Legs. The player does not have to dodge to leave the square he starts in. If the player successfully makes the D6 roll then he makes a perfect jump and may carry on moving. If the player fails the Agility roll then he is Knocked Down in the square that he was leaping to, and the opposing coach makes an Armour roll to see if he was injured. A player may only use the Leap skill once per turn.",
                "es": "Un jugador con esta habilidad puede elegir saltar sobre cualquier casilla adyacente a una casilla libre u ocupada por un jugador en pie o tumbado, siguiendo las reglas de brincar. Reduce en 1 el modificador para Brincar o Saltar hasta un mínimo de -1. Un jugador con la Habilidad Pogo Saltarín no puede aprender Saltar."
            }
        },
        // {
        //     "id": "perk-cannoneer",
        //     "name": {
        //         "en": "Cannoneer",
        //         "es": "Cañonero"
        //     },
        //     "family": "Passing",
        //     "description": {
        //         "en": "When this player performs a Long Pass action or a Long Bomb Pass action, you may apply an additional +1 modifier to the Passing Ability test.",
        //         "es": "Cuando este jugador realiza un Pase Largo o Bomba Larga puede añadir +1 a la tirada de Pase."
        //     }
        // },
        {
            "id": "perk-leader",
            "name": {
                "en": "Leader",
                "es": "Líder"
            },
            "family": "Passing",
            "description": {
                "en": "A team which has one or more players with this Skill gains a single extra team re-roll, However, the Leader re-roll can only be used if there is at least one player with this Skill on the pitch (even if the player with this Skill is Prone, Stunned or has lost their Tackle Zone). If all players with this Skill are removed from play before the Leader re-roll is used, is lost. The Leader Re-roll can be carried over into extra time if it is not used, but the team does not receive a new one at the start of extra time. Unlike standard Team Re-rolls, the Leader Re-roll cannot be lost due to a Halfling Master Chef. Otherwise, the Leader re-roll is treated just like a normal team re-roll.",
                "es": "Un equipo con un jugador con esta habilidad gana un Re-Roll de Líder, sólo puede usarse si un jugador con esta habilidad está en el campo, si el jugador sale del campo antes de haber usado esta Re-Roll, se pierde. Este Re-Roll puede usarse en la Prórroga si no se ha gastado. Esta Re-Roll no puede perderse con el Chef Halfling."
            }
        },
        {
            "id": "perk-nerves-of-steel",
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
            "id": "perk-cloud-burster",
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
            "id": "perk-pass",
            "name": {
                "en": "Pass",
                "es": "Pasar"
            },
            "family": "Passing",
            "description": {
                "en": "A player with the Pass skill is allowed to re-roll the D6 if he throws an inaccurate pass or fumbles.",
                "es": "Este jugador puede repetir una tirada fallida de Pase cuando hace una Acción de Pase."
            }
        },
        {
            "id": "perk-running-pass",
            "name": {
                "en": "Running Pass",
                "es": "Pase en carrera"
            },
            "family": "Passing",
            "description": {
                "en": "If this player performs a Quick Pass action, their activation does not have to end once the pass is resolved. If you wish and if this player has not used their full Movement Allowance, they may continue to move after resolving the pass.",
                "es": "(Running Pass) Cuando este jugador realiza un Pase Rápido, puede continuar moviendo después de efectuar el Pase."
            }
        },
        {
            "id": "perk-hail-mary-pass",
            "name": {
                "en": "Hail Mary Pass",
                "es": "Pase a lo Loco"
            },
            "family": "Passing",
            "description": {
                "en": "The player may throw the ball to any square on the playing pitch, no matter what the range: the range ruler is not used. Roll a D6. On a roll of 1 the player fumbles the throw, and the ball will bounce once from the thrower’s square. On a roll of 2-6, the player may make the pass. The Hail Mary pass may not be intercepted, but it is never accurate – the ball automatically misses and scatters three squares. Note that if you are lucky, the ball will scatter back into the target square! This skill may not be used in a Blizzard or with the Throw Team-Mate skill.",
                "es": "(Hail Mary Pass) Cuando este jugador realice una acción de Pase (o Lanzar Bomba) puede elegir cualquier casilla del campo como objetivo. Independientemente del resultado de la tirada de PA, nunca será un Pase Preciso, pero es necesario hacer la tirada para determinar si el pase es Balón Perdido o Muy Impreciso. Un Pase a lo Loco no puede Interferirse ni ser usado con Ventisca."
            }
        },
        {
            "id": "perk-safe-pass",
            "name": {
                "en": "Safe Pass",
                "es": "Pase Seguro"
            },
            "family": "Passing",
            "description": {
                "en": "Should This player fumble a Pass Action, the ball is not dropped, does not bounce from the square this player occupies, and no Turnover is caused. Instead, this player retains possession of the ball and their activation ends.",
                "es": "(Safe Pass) Cuando este jugador obtiene un resultado de Balón Perdido en una acción de Pase, el balón no rebota y no causa cambio de turno, el balón se queda en posesión del Lanzador y acaba su acción inmediatamente."
            }
        },
        {
            "id": "perk-accurate",
            "name": {
                "en": "Accurate",
                "es": "Precisión"
            },
            "family": "Passing",
            "description": {
                "en": "The player may add 1 to the D6 roll when he passes.",
                "es": "Cuando este jugador realiza un Pase Rápido o Pase Corto puede añadir +1 a la tirada de Pase."
            }
        },
        {
            "id": "perk-break-tackle",
            "name": {
                "en": "Break Tackle",
                "es": "Abrirse Paso"
            },
            "family": "Strength",
            "description": {
                "en": "Once during their activation, after making an Agility test in order to Dodge, this player may modify the dice roll by +1 if their Strength characteristic is 4 or less, or by +2 if their Strength characteristic is 5 or more.",
                "es": "(Break Tackle) Una vez por activación, tras hacer un chequeo de agilidad para esquivar, este jugador modifica la tirada del dado en +1 si su atributo fuerza es de 4 o menos, o en +2 si su atributo fuerza es de 5 o más."
            }
        },
        {
            "id": "perk-grab",
            "name": {
                "en": "Grab",
                "es": "Apartar"
            },
            "family": "Strength",
            "description": {
                "en": "A player with this skill uses his great strength and prowess to grab his opponent and throw him around. To represent this, only while making a Block Action, if his block results in a push back he may choose any empty square adjacent to his opponent to push back his opponent. When making a Block or Blitz Action, Grab and Side Step will cancel each other out and the standard pushback rules apply. Grab will not work if there are no empty adjacent squares. A player with the Grab skill can never learn or gain the Frenzy skill through any means. Likewise, a player with the Frenzy skill can never learn or gain the Grab skill through any means.",
                "es": "Cuando este jugador realiza una acción de Placaje (en sí misma o como parte de una acción de penetración), puede utilizar la habilidad de Apartar para impedir que el blanco del placaje utilice a su vez la habilidad de Echarse a un lado. Además, cuando este jugador realice una acción de placaje (que no sea parte de una acción de penetración), si el blanco resulta empujado puedes elegir cualquier casilla desocupada adyacente al blanco y empujarlo allí. Si no hay casillas desocupadas adyacentes al blanco, esta habilidad no puede utilizarse. Un jugador con esta habilidad no puede tener la habilidad de furia."
            }
        },
        {
            "id": "perk-strong-arm",
            "name": {
                "en": "Strong Arm",
                "es": "Brazo Fuerte"
            },
            "family": "Strength",
            "description": {
                "en": "This player may apply a +1 modifier to any Passing Ability test rolls they make when performing a Throw Team-mate action. A player that does not have the Throw team-mate trait cannot have this Skill.",
                "es": "(Strong Arm) Este jugador puede aplicar un modificador de +1 a cualquier chequeo de pase que efectué al realizar una acción de Lanzar Compañero. Un jugador que no tenga el rasgo lanzar compañero no puede tener esta habilidad."
            }
        },
        {
            "id": "perk-thick-skull",
            "name": {
                "en": "Thick Skull",
                "es": "Cabeza Dura"
            },
            "family": "Strength",
            "description": {
                "en": "When an Injury roll is made against this player (even if this player is Prone, Stunned or has lost their Tackle Zone), they can only be KO’d on a roll of 9, and will treat a roll of 8 as stunned result. If this player also has the Stunty trait, they can only be KO’d on a roll of 8, and will treat a roll of 7 as Stunned result. All other results are unaffected.",
                "es": "(Thick Skull) Cuando se haga una tirada de heridas contra este jugador ( incluso si esta tumbado boca arriba, aturdido o ha perdido su zona de defensa), solo quedara Inconsciente con un resultado de 9, y tratara el resultado de 8 como Aturdido. En cambio, si este jugador tienes además el rasgo Escurridizo, solo quedara inconsciente con un resultado de 8, y tratara el resultado de 7 como aturdido. Los demás resultados de la tabla de heridas no se ven afectados por la habilidad Cabeza Dura."
            }
        },
        {
            "id": "perk-pile-driver",
            "name": {
                "en": "Pile Driver",
                "es": "Crujir"
            },
            "family": "Strength",
            "description": {
                "en": "When an opposition player is Knocked Down by this player as the result of a Block action (on its own or as part of a Blitz action), this player may immediately commit a free Foul action against the Knocked Down player. To use this Skill, this player must be Standing after the block dice result has been selected and applied, and must occupy a square adjacent to the Knocked Down player, After using this Skill, this player is Placed Prone and their activation ends immediately.",
                "es": "(Pile Driver) Cuando un jugador rival sea Derribado por este jugador debido a una acción de Placaje (sea o no parte de una acción de penetración), este jugador puede cometer de inmediato una acción de falta gratuita contra el jugador al que acaba de derribar. Para poder utilizar esta habilidad, este jugador debe estar en pie tras elegir y aplicar el resultado de los dados de placajes, y además debe ocupar una casilla adyacente al jugador rival derribado. Tras utilizar esta habilidad, este jugador se coloca Tumbado boca arriba y su activación finaliza inmediatamente."
            }
        },
        {
            "id": "perk-guard",
            "name": {
                "en": "Guard",
                "es": "Defensa"
            },
            "family": "Strength",
            "description": {
                "en": "A player with this skill assists an offensive or defensive block even if he is in another player’s tackle zone. This skill may not be used to assist a foul.",
                "es": "Cuando un jugador realiza una Acción de Placaje (incluyendo como parte de una Acción de Blitz) este jugador puede ofrecer asistencias tanto ofensivas como defensivas independientemente de cuántos jugadores rivales los estén Marcando."
            }
        },
        {
            "id": "perk-mighty-blow",
            "name": {
                "en": "Mighty Blow",
                "es": "Golpe Mortífero"
            },
            "family": "Strength",
            "description": {
                "en": "Add 1 to any Armour or Injury roll made by a player with this skill when an opponent is Knocked Down by this player during a block. Note that you only modify one of the dice rolls, so if you decide to use Mighty Blow to modify the Armour roll, you may not modify the Injury roll as well. Mighty Blow cannot be used with the Stab or Chainsaw skills.",
                "es": "(Mighty Blow) Cuando este jugador realiza una acción de Placaje (sea o no parte de una acción de penetración) que tiene como resultado que un jugador rival sea derribado, puedes modificar o bien la tirada de armadura o bien la tirada de heridas en una cantidad igual al numero indicado entre paréntesis. Esta habilidad no puede utilizarse en combinación con los rasgos apuñalar o motosierra."
            }
        },
        {
            "id": "perk-juggernaut",
            "name": {
                "en": "Juggernaut",
                "es": "Imparable"
            },
            "family": "Strength",
            "description": {
                "en": "A player with this skill is virtually impossible to stop once he is in motion. If this player takes a Blitz Action, the opposing player may not use his Fend, Stand Firm or Wrestle skills against the Juggernaut player’s blocks. The Juggernaut player may also choose to treat a !Both Down’ result as if a !Pushed’ result has been rolled instead for blocks he makes during a Blitz Action.",
                "es": "Cuando este jugador realiza un placaje como parte de una acción de penetración (pero no una acción de Placaje en sí misma), puedes elegir tratar un resultado de Ambos jugadores derribados como resultado de Empujón. Además, cuando este jugador realiza una acción de placaje como parte de acción de penetración, el blanco de dicho placaje no puede usar habilidades de Forcejeo, Mantenerse firme ni Zafarse."
            }
        },
        {
            "id": "perk-arm-bar",
            "name": {
                "en": "Arm Bar",
                "es": "Llave de Brazo"
            },
            "family": "Strength",
            "description": {
                "en": "If an opposition player Falls Over as a result of failing their Agility test when attempting to Dodge, Jump or Leap out of a square in which they were being Marked by this player, you may apply a +1 modifier to either the armour roll or Injury roll. This modifier may be applied after the roll has been made and may be applied even if this player is row Prone. If the opposition player was being marked by more than one player with this Skill, only one player may use it.",
                "es": "(Arm Bar) Si un jugador rival cae por haber fallado su chequeo de agilidad al intentar Esquivar, Saltar o Brincar para salir de una casilla en la que esta siendo marcado por este jugador, puede aplicar un modificador de +1 o bien a la tirada de armadura o bien a la tirada de herida. Este modificador puede aplicarse tras hacer la tirada en cuestión y puede aplicarse incluso si este jugador está ahora tumbado boca abajo. Si el jugador rival esta siendo marcado a la vez por varios jugadores con esta habilidad, solo uno de ellos podrá utilizarla."
            }
        },
        {
            "id": "perk-brawler",
            "name": {
                "en": "Brawler",
                "es": "Luchador"
            },
            "family": "Strength",
            "description": {
                "en": "When this player performs a Block action on its own (but not as part of a Blitz Action), this player may re-roll a single Both Down result.",
                "es": "Cuando este jugador realiza una acción de Placaje (que NO sea parte de un Blitz), puede repetir un único dado con resultado de ambos jugadores derribados."
            }
        },
        {
            "id": "perk-stand-firm",
            "name": {
                "en": "Stand Firm",
                "es": "Mantenerse Firme"
            },
            "family": "Strength",
            "description": {
                "en": "This player may choose not to be pushed back, either as the result of a Block action made against them or by a chain-push. Using this Skill does not prevent an opposition player with the Frenzy Skill from performing a second Block action if this player is still Standing after the first.",
                "es": "(Stand Firm) Este jugador puede elegir no ser empujado, ya sea como resultado de una acción de placaje contra él o debido a un empujón en cadena. El uso de  esta habilidad no impide a un jugador rival con la habilidad furia realizar una segunda acción de placaje contra este jugador, si este jugador sigue en pie tras el primer placaje."
            }
        },
        {
            "id": "perk-multiple-block",
            "name": {
                "en": "Multiple Block",
                "es": "Placaje Múltiple"
            },
            "family": "Strength",
            "description": {
                "en": "At the start of a Block Action a player who is adjacent to at least two opponents may choose to throw blocks against two of them. Make each block in turn as normal except that each defender’s strength is increased by 2. The player cannot follow up either block when using this skill, so Multiple Block can be used instead of Frenzy, but both skills cannot be used together. To have the option to throw the second block the player must still be on his feet after the first block.",
                "es": "(Multiple Block) Cuando este jugador realiza una acción de Placaje (que no sea parte de una acción de penetración), puede elegir efectuar dos acciones de Placaje, cada una de ellas tomando como blanco a un jugador rival distinto al que este marcando. No obstante, al hacer esto el atributo fuerza de este jugador se reduce en 2 durante el resto de esa activación. Ambas acciones de placaje se efectúan de manera simultánea, lo que quiere decir que se resuelve por completo incluso aunque una de ellas (o las dos) provoque un cambio de turno. A fin de evitar confusiones, las tiradas para cada acción de Placaje deberían mantenerse separadas. Este jugador no puede hacer movimientos de impulso al utilizar esta habilidad. Ten en cuenta que elegir utilizar esta habilidad significa que este jugador no podrá utilizar la habilidad Furia durante la misma activación."
            }
        },
        {
            "id": "perk-foul-appearance",
            "name": {
                "en": "Foul Appearance",
                "es": "Apariencia Asquerosa"
            },
            "family": "Mutation",
            "description": {
                "en": "When an opposition player declares a Block action targeting this player (on its own or as part of a Blitz action), or any Special actions that targets this player, their coach must firs roll a D6, even if this player has lost their Tackle Zone. On a roll of 1, the player cannot perform the declared action and the action is wasted. This Skill may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                "es": "(Foul Appearance) Cuando un jugador contrario declara una acción de Placaje dirigida a este jugador (por sí sola o como parte de una acción Blitz), o cualquier acción Especial dirigida a este jugador, su entrenador debe tirar primero un dado D6, incluso si este jugador ha perdido su Zona de Defensa. Con una tirada de 1, el jugador no puede realizar la acción declarada y la acción se desperdicia. Esta habilidad puede seguir usándose si el jugador está tumbado o ha perdido su Zona de Defensa."
            }
        },
        {
            "id": "perk-monstrous-mouth",
            "name": {
                "en": "Monstrous Mouth",
                "es": "Boca Monstruosa"
            },
            "family": "Mutation",
            "description": {
                "en": "This player may re-roll any failed attempt to catch the ball. In addition, the Strip Ball skill cannot be used against this player.",
                "es": "(Monstrous Mouth) El jugador puede repetir cualquier intento de Atrapar el balón, además no se puede usar Robar Balón contra este jugador."
            }
        },
        {
            "id": "perk-extra-arms",
            "name": {
                "en": "Extra Arms",
                "es": "Brazos Adicionales"
            },
            "family": "Mutation",
            "description": {
                "en": "A player with one or more extra arms may add 1 to any attempt to pick up, catch or intercept.",
                "es": "(Extra Arms) Este jugador puede aplicar +1 cuando intenta coger el balón del suelo, Atrapar Balón o Interferir un pase."
            }
        },
        {
            "id": "perk-prehensile-tail",
            "name": {
                "en": "Prehensile Tail",
                "es": "Cola Prensil"
            },
            "family": "Mutation",
            "description": {
                "en": "When an active opposition player attempts to Dodge, Jump or Leap in order to vacate a square in which they are being Marked by this player, there is an additional -1 modifier applied to the active player’s Agility test. If the opposition player is being Marked by more than one player with this Mutation, only one player may use it.",
                "es": "(Prehensile Tail) Cuando un jugador rival intenta esquivar, saltar o brincar para abandonar una casilla en la que está siendo marcado por este jugador, se aplica un modificador adicional de -1 a la prueba de Agilidad del jugador activo. Si el jugador contrario está siendo marcado por más de un jugador con esta Mutacion, sólo un jugador puede usarla."
            }
        },
        {
            "id": "perk-horns",
            "name": {
                "en": "Horns",
                "es": "Cuernos"
            },
            "family": "Mutation",
            "description": {
                "en": "A player with Horns may use them to butt an opponent. Horns adds 1 to the player’s Strength for any block(s) he makes during a Blitz Action.",
                "es": "Cuando el jugador realiza una acción de Placaje como parte de una acción Blitz (pero no por sí sola), puedes aplicar un modificador +1 a la característica de Fuerza de este jugador. Este modificador se aplica antes de contar las asistencias, antes de aplicar cualquier otro modificador de Fuerza y antes de usar cualquier otra Habilidad o Rasgo."
            }
        },
        {
            "id": "perk-two-heads",
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
            "id": "perk-claws",
            "name": {
                "en": "Claws",
                "es": "Garras"
            },
            "family": "Mutation",
            "description": {
                "en": "A player with this skill is blessed with a huge crab-like claw or razor sharp talons that make armour useless. When an opponent is Knocked Down by this player during a block, any Armour roll of 8 or more after modifications automatically breaks armour.",
                "es": "Cuando hagas una tirada de Armadura contra un rival que haya sido derribado como resultado de una acción de Placaje o Blitz hecha por este jugador, con 8+ antes de aplicar modificadores superará la tirada de Armadura."
            }
        },
        {
            "id": "perk-big-hand",
            "name": {
                "en": "Big Hand",
                "es": "Mano Grande"
            },
            "family": "Mutation",
            "description": {
                "en": "One of the player’s hands has grown monstrously large, yet remained completely functional. The player ignores modifier(s) for enemy tackle zones or Pouring Rain weather when he attempts to pick up the ball.",
                "es": "(Big Hand) Este jugador puede ignorar los modificadores negativos por zonas de defensa o por las condiciones climáticas de lluvia torrencial al intentar coger el balón del suelo."
            }
        },
        {
            "id": "perk-iron-hard-skin",
            "name": {
                "en": "Iron Hard Skin",
                "es": "Piel Ferrea"
            },
            "family": "Mutation",
            "description": {
                "en": "The Claws skill cannot be used when making an armour roll against this player. This Skill may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                "es": "(Iron Hard Skin) La habilidad Garras no puede usarse al hacer una tirada de armadura contra este jugador. Esta habilidad aún puede usarse si el jugador está Tumbado, Aturdido, o ha perdido su Zona de Defensa."
            }
        },
        {
            "id": "perk-very-long-legs",
            "name": {
                "en": "Very Long Legs",
                "es": "Piernas Muy Largas"
            },
            "family": "Mutation",
            "description": {
                "en": "This player may reduce any negative modifier applied to the Agility test when they attempt to Jump over a Prone or Stunned player (or to Leap over an empty square or a square occupied by a Standing player, if this player has the Leap Skill) by 1, to a minimum of -1. Additionally, this player may apply a +2 modifier to any attempts to interfere with a pass they make. Finally this player ignores the Cloud Burster skill.",
                "es": "(Very Long Legs) Este jugador puede reducir en 1 cualquier modificador negativo aplicado a la prueba de Agilidad cuando intente saltar sobre un jugador Tumbado boca arriba o Aturdido (o saltar sobre una casilla vacía o una casilla ocupada por un jugador de pie, si este jugador tiene la habilidad Saltar), hasta un mínimo de -1. Además, este jugador puede aplicar un modificador de +2 a cualquier intento de interferir en un pase que realice. Por último, este jugador ignora la habilidad Parte Nubes."
            }
        },
        {
            "id": "perk-disturbing-presence",
            "name": {
                "en": "Disturbing Presence",
                "es": "Presencia Perturbadora"
            },
            "family": "Mutation",
            "description": {
                "en": "This player’s presence is very disturbing, whether it is caused by a massive cloud of flies, sprays of soporific musk, an aura of random chaos or intense cold, or a pheromone that causes fear and panic. Regardless of the nature of this mutation, any player must subtract 1 from the D6 when they pass, intercept or catch for each opposing player with Disturbing Presence that is within three squares of them, even if the Disturbing Presence player is Prone or Stunned.",
                "es": "(Disturbing Presence) Cuando un oponente intente hacer una acción de Pase, Lanzar Compañero, Lanzar Bomba, Interferir Pase o Atrapar balón debe aplicar un -1 por cada jugador con esta habilidad que se encuentra a 3 casillas o menos. Incluso si está Tumbado en el suelo o ha perdido su Zona de Defensa."
            }
        },
        {
            "id": "perk-tentacles",
            "name": {
                "en": "Tentacles",
                "es": "Tentáculos"
            },
            "family": "Mutation",
            "description": {
                "en": "This player can use this Skill when an opposition player they are Marking voluntarily moves out of a square within this player’s Tackle Zone. Roll a D6, adding the ST of this player to the roll and then subtracting the ST of the opposition player. If the result is 6 or higher, or if the roll is a natural 6, the opposition player is held firmly in place and their movement comes to an end. If, however, the result is 5 or lower, or if the roll is a natural 1, this Skill has no further effect. A player may use this Skill any number or times per turn, during either team’s turn. If an opposition player is being Marked by more than one player with this Skill, only one player may use it.",
                "es": "Este jugador puede usar esta habilidad cuando un jugador contrario al que está marcando se desplaza voluntariamente fuera de una casilla dentro de su zona de placaje. Tira un D6, sumando la Fuerza de este jugador a la tirada y restando la Fuerza del jugador contrario. Si el resultado es 6 o más, o si la tirada es un 6 natural, el jugador adversario es retenido firmemente en su sitio y su movimiento finaliza. Sin embargo, si el resultado es 5 o inferior, o si la tirada es un 1 natural, esta Habilidad no tiene ningún efecto. Un jugador puede usar esta Habilidad cualquier número de veces por turno, durante el turno de cualquiera de los dos equipos. Si un jugador contrario está siendo marcado por más de un jugador con esta habilidad, sólo un jugador puede usarla."
            }
        },
        {
            "id": "perk-animal-savagery",
            "name": {
                "en": "Animal Savagery",
                "es": "Animal Feroz"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before peforming the action, roll a D6, applying a +2 modifier to the dice roll if you declared the player would perform a Block or Blitz action (or a Special action granted by a Skill or Trait that can be performed instead of a Block action): If you declared that this player would perform an action which can only be performed once per team turn and this player’s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                "es": "(Animal Savagery) Cuando se activa a este jugador y se declara una acción, incluso si está tumbado o sin zona de defensa, debe tirar 1d6, sumando +2 si la acción declarada es Placaje, Blitz o Habilidad Especial que sustituya al Placaje. \n1-3, Un jugador amigo en pie y adyacente, se tumba boca arriba, no causa cambio de turno a menos que llevase el balón. Después debe tirar contra su Armadura, el rival puede usar a su gusto cualquier habilidad aplicable que posea.Una vez resuelto esto puede continuar ejecutando su acción declarada normalmente.Si no hay jugador amigo en pie y adyacente, el jugador perderá su acción declarada y perderá su zona de defensa. Si no hay jugador amigo en pie y adyacente, el jugador perderá su acción declarada y perderá su zona de defensa. 4+, el jugador continúa su acción normalmente. Si declaraste que este jugador realizaría una acción que sólo puede realizarse una vez por turno de equipo y la activación de este jugador terminó antes de que la acción pudiera completarse, la acción se considera realizada y ningún otro jugador de tu equipo puede realizar la misma acción este turno de equipo."
            }
        },
        {
            "id": "perk-animosity",
            "name": {
                "en": "Animosity",
                "es": "Animosidad"
            },
            "family": "Extraordinary",
            "description": {
                "en": "This player is jealous of and dislikes certain other players of their team, as shown in brackets after the name of the Skill on this player’s profile. This may be defined by position or race. For example, a Skaven Thrower on an Underworld Denizens team has Animosity (Underworld Goblin Lineman), meaning they suffer Animosity towards any Underworld Goblin Lineman players on their team, Whereas a Skaven Renegade on a Chaos Renegade team has Animosity (all team-mates), meaning they suffer Animosity towards all of their team-mates equally. When this player wishes to perform a Hand-off action to a team-mate of the type listed, or attempts to perform a Pass action and the target square is occupied by a team-mate of the type listed, this player may refuse to do so. Roll a D6. On a roll of 1, this player refuses to perform the action and their activation comes to an end. Animosity does not extend to Mercenaries or Star Players.",
                "es": "Cuando este jugador desea hacer una Entrega en Mano o un Pase a un jugador listado en (x), debe tirar 1D6, con un resultado de 1 el jugador se queda con el balón y termina su activación. No se aplica a Mercenarios ni a Jugadores Estrella."
            }
        },
        {
            "id": "perk-stab",
            "name": {
                "en": "Stab",
                "es": "Apuñalar"
            },
            "family": "Extraordinary",
            "description": {
                "en": "Instead of performing a Block action (on its own or as part of a Blitz action), this player may perform a ‘Stab’ Special action. Exactly as described for a Block action, nominate a single Standing player to be the target of the Stab Special action. There is no limit to how many players with this Trait may perform this Special action each team turn.To perform a Stab Special action, make an unmodified Armour roll against the target: \nIf the Armour of the player hit is broken, they become Prone and an Injury roll is made against them, This Injury roll cannot be modified in any way. If the Armour of the player hit is not broken, this Trait has no effect. If Stab is used as part of a Blitz action, the player cannot continue moving after using it.",
                "es": "En lugar de realizar una acción de Placaje o Blitz, puede elegir un oponente y hacer esta acción especial, debe tirar por Armadura y Heridas normalmente, ninguna de estas tiradas puede ser modificada de ninguna manera, si no supera la tirada de Armadura, no tiene efecto. Si forma parte de un Blitz no puede seguir moviendo."
            }
        },
        {
            "id": "perk-secret-weapon",
            "name": {
                "en": "Secret Weapon",
                "es": "Arma Secreta"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When a drive in which this player took part ends, even if this player was not on the pitch at the end of the drive, this player will be Sent-off for committing a Foul, as described on page 63.",
                "es": "(Secret Weapon) Cuando termine la entrada en la que este jugador haya participado, incluso si ya no se encuentra en el campo al finalizar dicha entrada, este jugador será expulsado por el árbitro como si hubiera cometido una Falta."
            }
        },
        {
            "id": "perk-cannoneer",
            "name": {
                "en": "Cannoneer",
                "es": "Bombardero"
            },
            "family": "Passing",
            "description": {
                "en": "When this player performs a Long Pass action or a Long Bomb Pass action, you may apply an additional +1 modifier to the Passing Ability test.",
                "es": "Cuando se activa este jugador y está en pie, puede efectuar una acción especial de Lanzamiento de Bomba, esta acción No se considera ni Pase ni Lanzamiento de Compañero, pero sólo se puede ejecutar un Lanzamiento de Bomba por turno. Una Bomba puede ser Lanzada, Atrapada e Interferida igual que un balón, usando las reglas habituales de Pase con las siguientes excepciones: \nUn jugador no puede levantarse o moverse antes de Lanzar una Bomba. La Bomba no rebota nunca, se mantiene en la casilla destinada. Si un jugador falla al atraparla, se mantendrá en la casilla ocupada por el jugador. Si el Lanzamiento de Bomba es un Fumble, explotará inmediatamente en la casilla ocupada por el Lanzador. Si la Bomba cae en una casilla vacía o atrapada por un rival no causa cambio de turno. Un jugador en posesión del balón puede también coger una bomba. Cualquier habilidad usada para realizar un Pase (PA) puede usarse para Lanzar una Bomba, excepto En la Bola. Si la Bomba es atrapada por algún jugador tira 1d6: \n4+, la Bomba explota como se describe a continuación. 1-3, el jugador debe Lanzar la Bomba inmediatamente. Si la Bomba abandona el campo, explota en el público y se pierde. Cuando la Bomba cae en el suelo, sobre un jugador tumbado o en casilla ocupada por jugador y falla al atrapar, explota. – Si la Bomba explota en una casilla ocupada, el jugador es inmediatamente impactado. – Tira 1d6 por cada jugador adyacente a la casilla donde explota la Bomba. 4+, el jugador es impactado. 1-3, el jugador evita la explosión. Cualquier jugador en pie impactado por la Bomba, se tumba en el suelo. Se debe tirar por Armadura y Heridas si corresponde con un modificador de +1 a la Armadura o Heridas. Igualmente, para los jugadores tumbados impactados."
            }
        },
        {
            "id": "perk-titchy",
            "name": {
                "en": "Titchy",
                "es": "Canijo"
            },
            "family": "Extraordinary",
            "description": {
                "en": "This player may apply a +1 modifier to any Agility tests they make in order to Dodge. However, if an opposition player dodges into a square within the Tackle Zone of this player, this player does not count as Marking the moving player for the purpose of calculating Agility test modifiers.",
                "es": "Este jugador puede aplicar un +1 a la tirada de AG al Esquivar, además cuando un oponente intenta Esquivar a una zona de defensa de un jugador con esta habilidad no aplica modificadores negativos de AG al esquivarle."
            }
        },
        {
            "id": "perk-swarming",
            "name": {
                "en": "Swarming",
                "es": "Colarse"
            },
            "family": "Extraordinary",
            "description": {
                "en": "During each Start of Drive sequence, after Step 2 but before Step 3, you may remove D3 players with this Trait from the Reserves box of your dugout and set them up on the pitch, allowing you to set up more than the usual 11 players. These extra players may not be placed on the Line of Scrimmage or in a Wide Zone. Swarming players must be set up in their team’s half.When using Swarming, a coach may not set up more players with the Swarming trait onto the pitch than the number of friendly players with the Swarming trait that were already set up. So, if a team had 2 players with the Swarming trait already set up on the pitch, and then rolled for 3 more players to enter the pitch via Swarming, only a maximum of 2 more Swarming players could be set up on the pitch.",
                "es": "Durante el inicio de cada entrada, después del paso 2 (Colocar el Balón y Desviar) pero antes del paso 3 (Tirar la tabla de Patada Inicial), puedes retirar 1d3 jugadores con esta regla del banquillo de reservas y colocarlos en el campo, superando el límite de 11 jugadores en el campo, no pueden estar en las bandas ni en la línea frontal central."
            }
        },
        {
            "id": "perk-kick-team-mate",
            "name": {
                "en": "Kick Team-mate",
                "es": "Chutar Compañero"
            },
            "family": "Extraordinary",
            "description": {
                "en": "Once per team turn, in addition to another player performing either a Pass or a Throw Team-mate action, a single player with this Traits on the active team can perform a ‘Kick Team-mate’ Special action, follow the rules for Throw Team-mates actions as described on page 52.However, if the Kick Team-mate Special action is fumbled, the kicked player is automatically removed from play and an injury roll is made against them, treating a Stunned result as a KO’d result (note that, if the player that performed this action also has the Mighty Blow (+x) skill, the coach of the opposing team may use that Skill on this Injury roll). If the kicked player was in possession of the ball when removed from play, the ball will bounce from the square they occupied.",
                "es": "(Kick Team-mate) Una vez por turno, además de que otro jugador realice una acción de Pase o Lanzar Compañero, este jugador puede efectuar un Chutar Compañero. Para efectuarlo debes seguir las mismas reglas que con el Lanzar Compañero, pero si el resultado del Lanzamiento es un fumble, el jugador Pateado realiza tirada de Heridas, considerando el KO como resultado mínimo, además el entrenador rival puede hacer uso del Golpe Mortífero del Pateador si lo tuviera."
            }
        },
        {
            "id": "perk-decay",
            "name": {
                "en": "Decay",
                "es": "Descomposición"
            },
            "family": "Extraordinary",
            "description": {
                "en": "If this player suffers a Casualty result on the injury table, there is a +1 modifier applied to all rolls made against this player on the Casualty table.",
                "es": "Cuando este jugador tira en la tabla de Lesiones debe sumar +1 a dicha tirada."
            }
        },
        {
            "id": "perk-take-root",
            "name": {
                "en": "Take Root",
                "es": "Echar Raíces"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When this player is activated, even if they are Prone or have lost theio Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6: \nOn a roll of 1, this player becomes ‘Rooted’:A Rooted player cannot move from the square they currently occupy for any reason, voluntarily or otherwise, until the end of this drive, or until they are Knocked Down or Placed Prone.A Rooted player may perform any action available to them provided they can do so without moving. For example, a Rooted player may perform a Pass action but may not move before making the pass, and so on. A Rooted player cannot move from the square they currently occupy for any reason, voluntarily or otherwise, until the end of this drive, or until they are Knocked Down or Placed Prone. A Rooted player may perform any action available to them provided they can do so without moving. For example, a Rooted player may perform a Pass action but may not move before making the pass, and so on. On a roll of 2+, this player continues their activation as normal. If you declared that this player would perform any action that includes movement (Pass, Hand-off, Blitz or Foul) prior to them becoming Rooted, they may, complete the action if possible. If they cannot, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                "es": "(Take Root) Cuando se activa a este jugador y se declara una acción, incluso si está tumbado o sin zona de defensa, debe tirar 1D6: \n1, el jugador quedará enraizado, no podrá abandonar la casilla en la que se encontrase hasta el final de esta entrada, a menos que sea tumbado en el suelo. Un jugador enraizado puede realizar cualquier acción que no implique moverse. Cualquier acción declarada antes de enraizarse se considera realizada aunque no se lleve a cabo. 2+, el jugador continúa su acción normalmente."
            }
        },
        {
            "id": "perk-trickster",
            "name": {
                "en": "Trickster",
                "es": "Embaucador"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When a player is about to be hit by a Block action or a Special action that replaces a Block action (with the exception of a Block action caused by the Ball & Chain Move Special action), before determinig how many dice are rolled, they may be removed from the pitch ans placed in any other unoccupied square adjacent to the player performing the Block action.. The Block action then takes place as normal. If the player using this Trait is holding the ball and places themselves inthe opposition End Zone, the Block action will still be fully resolved before any touchdown is resolved.",
                "es": "Cuando un jugador está a punto de ser golpeado por una acción de Placaje o una acción que sustituye a una acción de Placaje (con la excepción de una acción de Placaje causada por la acción Especial de Movimiento de Bola con Cadena), antes de determinar cuántos dados se tiran, puede ser retirado del terreno de juego y colocado en cualquier otra casilla desocupada adyacente al jugador que realiza la acción de Placaje. Despues la acción de Placaje se realiza de forma normal. Si el jugador que utiliza este Rasgo tiene el balón en su poder y se coloca en la zona de TouchDown contraria, la acción de Bloqueo se resolverá por completo antes de que se resuelva cualquier TouchDown."
            }
        },
        {
            "id": "perk-stunty",
            "name": {
                "en": "Stunty",
                "es": "Escurridizo"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When this player makes an Agility test in order to Dodge, they ignore any -1 modifiers for being Marked in the square they have moved into, unless they also have either the Bombardier trait, the Chainsaw trait or the Swoop trait.However, when an opposition player attempts to interfere with a Pass action performed by this player, that player may apply a +1 modifier to their Agility test.Finally, player with this Trait are more prone to injury. Therefore, when an Injury roll is made against this player, roll 2D6 and consult the Stunty Injury table, on page 60. This Trait may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                "es": "Cuando este jugador hace una tirada de AG para Esquivar, puede ignorar todos los modificadores negativos por zonas de defensa enemigas, a menos que tenga la habilidad Bombardero, Motosierra o Planear. Además, cuando un rival intenta interferir un Pase hecho por este jugador, puede aplicar un +1 a la tirada de AG. También deben usar la Tabla de Heridas para Escurridizos."
            }
        },
        {
            "id": "perk-stakes",
            "name": {
                "en": "Stakes",
                "es": "Estacas"
            },
            "family": "Extraordinary",
            "description": {
                "en": "This player is armed with special stakes that are blessed to cause extra damage to the Undead and those that work with them. This player may add 1 to the Armour roll when they make a Stab attack against any player playing for a Khemri, Necromantic, Undead or Vampire team.",
                "es": "El jugador está armado con unas estacas especiales que están bendecidas para causar un daño adicional a los No Muertos y a aquéllos que trabajan para ellos. El jugador puede añadir 1 a la tirada de Armadura cuando realice un ataque con Puñal contra cualquier jugador que juegue para un equipo Khemri, Nigromantes, No Muertos o Vampiros."
            }
        },
        {
            "id": "perk-bone-head",
            "name": {
                "en": "Bone Head",
                "es": "Estúpido"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6: \nOn a roll of 1, this player forgets what they are doing and their activation ends immediately. Additionally, this player loses their Tackle Zone until they are next activated. On a roll of 2+, this player continues their activation as normal and completes their declared action. If you declared that this player would perform an action which can only be performed once per team turn and this player’s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                "es": "(Bone Head) Cuando se activa a este jugador y se declara una acción, incluso si está tumbado o sin zona de defensa, debe tirar 1d6: – 1, el jugador perderá su acción declarada y perderá su zona de defensa. – 2+, el jugador continúa su acción normalmente."
            }
        },
        {
            "id": "perk-fan-favorite",
            "name": {
                "en": "Fan Favorite",
                "es": "Favorito del Público"
            },
            "family": "Extraordinary",
            "description": {
                "en": "The fans love seeing this player on the pitch so much that even the opposing fans cheer for your team. For each player with Fan Favourite on the pitch your team receives an additional +1 FAME modifier (see page 18) for any Kick-Off table results, but not for the Winnings roll.",
                "es": "(Fan Favorite) Los hinchas adoran tanto ver a este jugador sobre el terreno de juego que incluso los hinchas contrarios animan a tu equipo. Por cada jugador Favorito del Público de tu equipo que se encuentra en el campo, tu equipo recibe un +1 adicional al modificador de FAMA para cualquier resultado de la Tabla de Patada Inicial, pero no para la tirada de Recaudación."
            }
        },
        {
            "id": "perk-right-stuff",
            "name": {
                "en": "Right Stuff",
                "es": "Humanoide Bala"
            },
            "family": "Extraordinary",
            "description": {
                "en": "If this player also has a Strength characteristic of 3 or less, they can be thrown by a team-mate with the Throw Team-mate skill, as described on page 52. This Trait may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                "es": "(Right Stuff) Si este jugador tiene FU 3 o inferior puede ser Lanzado por un Compañero de Equipo."
            }
        },
        {
            "id": "perk-unchannelled-fury",
            "name": {
                "en": "Unchannelled Fury",
                "es": "Ira Descontrolada"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6, applying a +2 modifier to the dice roll if you declared the player would perform a Block or Blitz action (or a Special action granted by a Skill or Trait that can be performed instead of a Block action) \nOn a roll of 1-3, this player rages incoherently at others but achieves little else. Their activation ends immediately. On a roll of 4+, this player continues their activation as normal and completes their declared action. If you declared that this player would perform an action which can only be performed once per team turn and this player’s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn. Take a look to all the teams on Blood Bowl!",
                "es": "(Unchannelled Fury) Cuando se activa a este jugador y se declara una acción, incluso si está tumbado o sin zona de defensa, debe tirar 1d6, sumando +2 si la acción declarada es Placaje, Blitz o Habilidad Especial. \n1-3, El jugador perderá su acción declarada. *No pierde zona de defensa.* 4+, el jugador continúa su acción normalmente."
            }
        },
        {
            "id": "perk-my-ball",
            "name": {
                "en": "My Ball",
                "es": "Mi Balón"
            },
            "family": "Extraordinary",
            "description": {
                "en": "A player with this Trait may not willingly give up the ball when in possession of it, and so may not make Pass actions, Hand-off actions, or use any other Skill or Trait that would allow them to relinquish possession of the ball. The only way they can lose possession of the ball is by being Knocked Down, Placed Prone, Falling Over or by the effect of a Skill, Trait or special rule of an opposing model.",
                "es": "(My Ball) Un jugador con este Rasgo no puede ceder voluntariamente el balón cuando está en posesión del mismo, por lo que no puede realizar acciones de Pase, Acciones de Entrega, ni utilizar ninguna otra Habilidad o Rasgo que le permita renunciar a la posesión del balón. La única forma de perder la posesión del balón es ser Derribado, Aturdido, Caerse o por el efecto de una Habilidad, Rasgo o regla especial de un jugador contrario."
            }
        },
        {
            "id": "perk-hypnotic-gaze",
            "name": {
                "en": "Hypnotic Gaze",
                "es": "Mirada hipnótica"
            },
            "family": "Extraordinary",
            "description": {
                "en": "The player has a powerful telepathic ability that he can use to stun an opponent into immobility. The player may use hypnotic gaze at the end of his Move Action on one opposing player who is in an adjacent square. Make an Agility roll for the player with hypnotic gaze, with a -1 modifier for each opposing tackle zone on the player with hypnotic gaze other than the victim’s. If the Agility roll is successful, then the opposing player loses his tackle zones and may not catch, intercept or pass the ball, assist another player on a block or foul, or move voluntarily until the start of his next Action or the drive ends. If the roll fails, then the hypnotic gaze has no effect.",
                "es": "(Hypnotic Gaze) Durante su activación puede hacer una acción especial de Mirada Hipnótica, declara el jugador en pie objetivo y en su zona de defensa, realiza una tirada de AG aplicando un -1 por cada zona de defensa enemiga. Si se supera la tirada el jugador pierde su zona de defensa hasta su siguiente activación. Una vez usada esta habilidad finaliza la activación del jugador. El jugador puede utilizar la Mirada Hipnótica al final de su Acción de Movimiento."
            }
        },
        {
            "id": "perk-chainsaw",
            "name": {
                "en": "Chainsaw",
                "es": "Motosierra"
            },
            "family": "Extraordinary",
            "description": {
                "en": "Instead of performing a Block action (on its own or as part of a Blitz action), this player may perform a “Chainsaw Attack” Special action. Exactly as described for a Block action, nominate a single Standing player to be the target of the Chainsaw Attack Special action, There is no limit to how many players with this Trait may perform this Special action each team turn.To perform a Chainsaw Attack Special action, roll a D6: \nOn a roll of 2+, the nominated target is hit by Chainsaw! On a roll of 1, the Chainsaw will violently ‘kick-back’ and hit the player wielding it. This will result in a Turnover. In either case, an Armour roll is made against the player hit by the Chainsaw, adding +3 to the result. If the armour of the player hit is broken, they become Prone and an Injury roll is made against them. This Injury roll cannot be modified in any way. If the armour of the player hit is not broken, this Trait has no effect This player can only use the Chainsaw once per turn (i.e., Chainsaw cannot be used with Frenzy or Multipe Block) and if used as part of a Blitz action, this player cannot continue moving after using it.If this player Fails Over or is Knocked Down, the opposing coach may add +3 to the Armour roll made against the player.If an opposition player performs a Block action targeting this player and a Player Down! or a POW! result is applied, +3 is added to the Armour roll. If a Both Down result is applied, +3 is added to both Armour rolls.Finally, this player may use their Chainsaw when they perform a Foul action. Roll a D6 for kick-back as described above. Once again, an Armour roll is made against the player hit by the Chainsaw. adding +3 to the score.",
                "es": "En lugar de efectuar una acción de Placaje o Blitz, este jugador puede hacer una acción especial de Motosierra, declara el objetivo del ataque y tira 1d6: \n2+, el objetivo es impactado por la Motosierra. 1, el atacante es impactado a sí mismo con la Motosierra. El jugador impactado por la Motosierra debe hacer una tirada de Armadura aplicando un +3 a la tirada. Si se supera la tirada de Armadura, se hace la tirada de Heridas, que no puede ser modificada de ninguna manera. Si no se supera la tirada de Armadura, el ataque no tiene efecto. El jugador sólo puede usar la Motosierra una vez por turno (no puede combinarse con Placaje Múltiple o Furia) Si el ataque forma parte de un Blitz no podrá continuar moviendo. Si un oponente realiza un placaje contra un jugador con Motosierra y resulta «Atacante Derribado» puede sumar +3 a la tirada de Armadura, así como si el resultado es «Ambos Derribados» ambos aplican +3 a la tirada de Armadura. Si el jugador comete Falta sobre un oponente tira 1d6 para ver si se impacta a sí mismo, si no aplica el +3 a la tirada de Armadura."
            }
        },
        {
            "id": "perk-swoop",
            "name": {
                "en": "Swoop",
                "es": "Planear"
            },
            "family": "Extraordinary",
            "description": {
                "en": "If this player is thrown by a team-mate, they do not scatter before landing as they normally would. Instead, you may place the Throw-in template over the player, facing towards either End Zone or either sideline as you wish. The player then moves from the target square D3 squares in a direction determined by rolling a D6 and referring to the Throw-in template.",
                "es": "Cuando este jugador es Lanzado por un Compañero no se dispersa normalmente antes de aterrizar, en cambio debes colocar la plantilla de Devolución de balón en dirección a la línea de Touchdown o una de las Bandas y avanzar 1d3 casillas en la dirección aleatoria marcada por la plantilla."
            }
        },
        {
            "id": "perk-pogo-stick",
            "name": {
                "en": "Pogo Stick",
                "es": "Pogo Saltarín"
            },
            "family": "Extraordinary",
            "description": {
                "en": "During their movement, instead of jumping over a single square that is occupied by a Prone or Stunned player, as described on page 45, a player with this Trait may choose to Leap over any single adjacent square, including unoccupied square and squares occupied by Standing players. Additionally, when this player makes and Agility test to jump over a Prone or Stunned player, or to Leap over an empty square or a square occupied by a Standing player, they may ignore any negative modifiers that would normally be applied for being Marked in the square they jumped or leaped from and/or for being marked in the square they have jumped or leaped into. A player with this Trait cannot also have the Leap skill.",
                "es": "(Pogo Stick) En lugar de intentar brincar a través de jugadores tumbados, además puede saltar a través jugadores en pie, se realiza de igual forma, pero ignorando todos los penalizadores. Un jugador con esta habilidad no puede tener Saltar."
            }
        },
        {
            "id": "perk-projectile-vomit",
            "name": {
                "en": "Projectile Vomit",
                "es": "Proyectil Vómito"
            },
            "family": "Extraordinary",
            "description": {
                "en": "Instead of performing a Block action (on its own or as part of a Blitz action), this player may perform a ‘Projectile Vomit’ Special action. Exactly as described for a Block action, nominate a single Standing player to be the target of the Projectile Vomit Special action. There is no limit to how many players with this Trait may perform this Special action each team turn.To perform a Projectile Vomit Special action, roll a D6: \nOn a roll of 2+, this player regurgitates acidic bile onto the nominated target. On a roll of 1, this player belches and snorts, before covering itself in acid bile. In either case, an armour roll is made against the player hit by the Projectile vomit. This Armour roll cannot be modified in any way. If the armour of the player hit is broken, they become Prone and an Injury roll is made against them. This Injury roll cannot be modified in any way. If the armour of the playerhit is not broken, this Trait has no effect. A player can only perform this Special action once per turn (i.e. Projectile Vomit cannot be used with Frenzy or Multiple Block).",
                "es": "(Projectile Vomit) En lugar de realizar una acción de Placaje o Blitz, puede elegir un oponente y hacer esta acción especial. Tira 1d6: \n1, el jugador se impacta a sí mismo. 2+, el jugador oponente es impactado. En cualquier caso, el jugador impactado debe tirar por Armadura normalmente. Si se supera la tirada de Armadura el jugador es tumbado boca arriba y se debe tirar por Heridas. Ninguna de estas tiradas puede ser modificada de ninguna manera, sino supera la tirada de Armadura, no tiene efecto."
            }
        },
        {
            "id": "perk-really-stupid",
            "name": {
                "en": "Really Stupid",
                "es": "Realmente Estúpido"
            },
            "family": "Extraordinary",
            "description": {
                "en": "When this player is activated, even if they are Prone or have lost their Tackle Zone, immediately after declaring the action they will perform but before performing the action, roll a D6, applying a +2 modifier to the dice roll if this player is currently adjacent to one or more Standing team-mates that do not have this Trait: \nOn a roll of 1-3, this player forgets what they are doing and their activation ends immediately. Additionally, this player loses their Tackle Zone until they are next activated. On a roll of 4+, this player continues their activation as normal and completes their declared action. Note that if you declared that this player would perform an action which can only be performed once per team turn and this player’s activation ended before the action could be completed, the action is considered to have been performed and no other player on your team may perform the same action this team turn.",
                "es": "(Really Stupid) Cuando se activa a este jugador y se declara una acción, incluso si está tumbado o sin zona de defensa, debe tirar 1d6, sumando +2 si está adyacente a un Compañero en pie que no sea Realmente Estúpido también: – 1-3, el jugador perderá su acción declarada y perderá su zona de defensa. – 4+, el jugador continúa su acción normalmente."
            }
        },
        {
            "id": "perk-regeneration",
            "name": {
                "en": "Regeneration",
                "es": "Regeneración"
            },
            "family": "Extraordinary",
            "description": {
                "en": "After a Casualty roll has been made against this player, roll a D6. On a roll of 4+, the Casualty roll is dicarded without effect and the player is placed in the Reserves box rather than the Casualty box of their team dugout. On a roll of 1-3, however, the result of the Casualty roll is applied as normal. This Trait may still be used if the player is Prone, Stunned, or has lost their Tackle Zone.",
                "es": "Si este jugador sufre una herida en la tabla de Lesiones, puedes ignorar el resultado con una tirada de 4+ exitosa. Si tiene éxito puedes poner al jugador en el banquillo en reservas."
            }
        },
        {
            "id": "perk-always-hungry",
            "name": {
                "en": "Always Hungry",
                "es": "Siempre Hambriento"
            },
            "family": "Extraordinary",
            "description": {
                "en": "If this player wishes to perform a Throw Team-mate action, roll a D6 after they have finished moving, but before they throw their team-mate. On a roll of 2+, continue with the throw as normal. On a roll of 1, this player will attempt to eat their team-mate. Roll another D6: \nOn a roll of 1, the team-mate has been eaten and is immediately removed from the Team Draft list. No apothecary can save them and no Regeneration attempts can be made. If the team-mate was in possession of the ball, it will bounce from the square the player occupies. On a roll of 2+, the team-mate squirms free and the Throw Team-mate action is automatically fumbled, as described on page 53.",
                "es": "(Always Hungry) Si este jugador desea Lanzar Compañero, tira 1d6 después de que haya movido. Con 2+ continúa la acción normalmente, con un resultado de 1, tira otro d6: – 1, se come al Compañero, no se puede usar Médico ni regeneración. Borra al jugador del Roster. – 2+, el Compañero se escapa y el resultado del Lanzamiento es automáticamente un fumble."
            }
        },
        {
            "id": "perk-no-hands",
            "name": {
                "en": "No Hands",
                "es": "Sin Manos"
            },
            "family": "Extraordinary",
            "description": {
                "en": "The player is unable to pick up, intercept or carry the ball and will fail any catch roll automatically, either because he literally has no hands or because his hands are full. If he attempts to pick up the ball then it will bounce, and will cause a turnover if it is his team’s turn.",
                "es": "(No Hands) Este jugador no puede intentar coger el balón del suelo, atrapar o interferir un pase. Si lo hace falla automáticamente y rebotará, además causará pérdida de turno si voluntariamente intenta cogerlo del suelo al entrar en la casilla del balón."
            }
        },
        {
            "id": "perk-loner",
            "name": {
                "en": "Loner",
                "es": "Solitario"
            },
            "family": "Extraordinary",
            "description": {
                "en": "If this player wishes to use a team re-roll, roll a D6. If you roll equal to or higher than the target number show in brackets, this player may use the team re-roll as normal. Otherwise, the original result stands without being re-rolled but the team re-roll is lost just as if it had been used. This Trait must still be used if the player is Prone or has lost their Tackle Zone.",
                "es": "Si este jugador desea hacer uso de una Re-Roll de equipo debe primero superar una tirada de Solitario (x+), de lo contrario no podrá repetir la tirada y perderá esa Re-Roll que deseaba usar."
            }
        }
    ]
);
