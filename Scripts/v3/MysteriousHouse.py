"""
Mysterious House Game for Amazon Alexa by Benjamin Dring
"""

from __future__ import print_function
import time
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session = False):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': '<speak>' + output + '</speak>'
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_audio_response(title, begin_output, audio_url, end_output, reprompt_text, should_end_session = False):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': '<speak>' + begin_output + '<audio src="' + audio_url + '"/>' + end_output + '</speak>'
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': begin_output + end_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_doubleaudio_response(title, begin_output, audio_url, mid_output, audio2_url, end_output,
                               reprompt_text, should_end_session = False):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': '<speak>' + begin_output + '<audio src="' + audio_url + '"/>' + mid_output +
                    '<audio src="' + audio2_url + '"/>' + end_output + '</speak>'
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': begin_output + mid_output + end_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_response(session_attributes, title, output, reprompt_text = None, should_end_session = False):
    return build_response(session_attributes, build_speechlet_response(
        title, output, reprompt_text, should_end_session))


def get_audio_response(session_attributes, title, begin_output, audio_url, end_output,
                       reprompt_text = None, should_end_session = False):
    return build_response(session_attributes, build_audio_response(
        title,  begin_output, audio_url, end_output, reprompt_text, should_end_session))


def get_doubleaudio_response(session_attributes, title, begin_output, audio_url, mid_output, audio2_url, end_output,
                              reprompt_text = None, should_end_session = False):
    return build_response(session_attributes, build_doubleaudio_response(
        title,  begin_output, audio_url, mid_output, audio2_url, end_output, reprompt_text, should_end_session))

# --------------- Database
def SetStartingData(userID):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('MysteriousHouse')
        table.put_item(
            Item={
                'UserID': userID,
                'CanWarp': False,
                'FloorNumber': 1,
                'LastUpdate': time.strftime("%Y-%m-%d")
            }
        )
    except ClientError as e1:
        print('Failed Database Access')

def LoadFloorNumber(userID):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('MysteriousHouse')
        response = table.get_item(
            Key={
                'UserID': userID
            }
        )
        if (len(response) < 2):
            SetStartingData(userID)
            return 1
        else:
            item = response['Item']
            floorNumber = item['FloorNumber']
            if (floorNumber < 0 or floorNumber > 3):
                SaveFloorNumber(userID, 1)
                return 1
            else:
                return floorNumber
    except ClientError as e1:
        try:
            SetStartingData(userID)
            return 1
        except ClientError as e2:
            return 1

def LoadCanWarp(userID):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('MysteriousHouse')
        response = table.get_item(
            Key={
                'UserID': userID
            }
        )
        if (len(response) < 2):
            SetStartingData(userID)
            return False
        else:
            item = response['Item']
            canWarp = item['CanWarp']
            return canWarp
    except ClientError as e1:
        try:
            SetStartingData(userID)
            return False
        except ClientError as e2:
            return False

def SaveFloorNumber(userID, floorNumber):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('MysteriousHouse')
        response = table.update_item(
            Key={
                'UserID': userID
            },
            UpdateExpression="set FloorNumber=:f, LastUpdate=:u",
            ExpressionAttributeValues={
                ':f': floorNumber,
                ':u': time.strftime("%Y-%m-%d")
            },
            ReturnValues = "UPDATED_NEW"
        )
    except ClientError as e:
        print('Update Failed')

def SaveCanWarp(userID, canWarp):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('MysteriousHouse')
        response = table.update_item(
            Key={
                'UserID': userID
            },
            UpdateExpression="set CanWarp=:c, LastUpdate=:u",
            ExpressionAttributeValues={
                ':c': canWarp,
                ':u': time.strftime("%Y-%m-%d")
            },
            ReturnValues = "UPDATED_NEW"
        )
    except ClientError as e:
        print('Update Failed')

def SaveAll(userID, canWarp, floorNumber):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('MysteriousHouse')
        response = table.update_item(
            Key={
                'UserID': userID
            },
            UpdateExpression="set CanWarp=:c, FloorNumber=:f, LastUpdate=:u",
            ExpressionAttributeValues={
                ':c': canWarp,
                ':f': floorNumber,
                ':u': time.strftime("%Y-%m-%d")
            },
            ReturnValues = "UPDATED_NEW"
        )
    except ClientError as e:
        print('Update Failed')


# --------------- Attributes

def construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry, spoken_to_larry, larry_asking):
    return {
        "Floor": 1,
        "X": x,
        "VisitedBarry": visited_barry,
        "VisitedLarry": visited_larry,
        "SpokenToLarry": spoken_to_larry,
        "SpokenToBarry": spoken_to_barry,  # after speaking to larry
        "LarryAsking": larry_asking,
    }


def get_starting_floor1_attributes():
    return construct_floor1_attributes(1, False, False, False, False, False)


def construct_floor2_attributes(x, y, osstate, mob_x, mob_y):
    return {
        "Floor":2,
        "X":x,
        "Y":y,
        "OState":osstate,  # OState is the orientation state (0 = starting, 1=facing north, 2=east, 3=south, 4=west)
        "MobX":mob_x, # Position of Haunted Armour
        "MobY":mob_y
    }


def get_starting_floor2_attributes():
    return  construct_floor2_attributes(0, 0, 0, 1, 1)


def get_starting_floor3_attributes():
    return {
        "Floor":3
    }


def get_floor_number(session):
    if session.get('attributes', {}) and "Floor" in session.get('attributes', {}):
        return session['attributes']['Floor']
    else:
        return -1


def get_x(session):
    if session.get('attributes', {}) and "X" in session.get('attributes', {}):
        return session['attributes']['X']
    else:
        return -1


def get_visited_barry(session):
    if session.get('attributes', {}) and "VisitedBarry" in session.get('attributes', {}):
        return session['attributes']['VisitedBarry']
    else:
        return -1


def get_visited_larry(session):
    if session.get('attributes', {}) and "VisitedLarry" in session.get('attributes', {}):
        return session['attributes']['VisitedLarry']
    else:
        return -1


def get_spoken_to_barry(session):
    if session.get('attributes', {}) and "SpokenToBarry" in session.get('attributes', {}):
        return session['attributes']['SpokenToBarry']
    else:
        return -1


def get_spoken_to_larry(session):
    if session.get('attributes', {}) and "SpokenToLarry" in session.get('attributes', {}):
        return session['attributes']['SpokenToLarry']
    else:
        return -1


def get_larry_asking(session):
    if session.get('attributes', {}) and "LarryAsking" in session.get('attributes', {}):
        return session['attributes']['LarryAsking']
    else:
        return -1


def get_y(session):
    if session.get('attributes', {}) and "Y" in session.get('attributes', {}):
        return session['attributes']['Y']
    else:
        return -1


def get_ostate(session):
    if session.get('attributes', {}) and "OState" in session.get('attributes', {}):
        return session['attributes']['OState']
    else:
        return -1


def get_mob_x(session):
    if session.get('attributes', {}) and "MobX" in session.get('attributes', {}):
        return session['attributes']['MobX']
    else:
        return -1


def get_mob_y(session):
    if session.get('attributes', {}) and "MobY" in session.get('attributes', {}):
        return session['attributes']['MobY']
    else:
        return -1

# --------------- Audio Files

def door_sound():
    return "https://www.benjamindring.co.uk/Resources/MysteriousHouse/Door.mp3"


def armour_sound():
    return "https://www.benjamindring.co.uk/Resources/MysteriousHouse/Armour.mp3"


def jingle_sound():
    return "https://www.benjamindring.co.uk/Resources/MysteriousHouse/FinishJingle.mp3"


def hatch_sound():
    return "https://www.benjamindring.co.uk/Resources/MysteriousHouse/HatchClose.mp3"


def jam_sound():
    return "https://www.benjamindring.co.uk/Resources/MysteriousHouse/Jam.mp3"

# --------------- Responses

def get_start_response():
    return get_audio_response(
        get_starting_floor1_attributes(),
        "You arrive at a mysterious house.",
        "You arrive at a mysterious house and open the front door. " ,
        door_sound(),
        "You see two more doors, one left and one right. "
        "Which door would you like to open first?",
        "Open the left or right door?"
    )

def initial_load_response(userID):
    floor_number = LoadFloorNumber(userID)
    if (floor_number == 1):
        return get_start_response()
    elif (floor_number == 2):
        return get_doubleaudio_response(
            get_starting_floor2_attributes(),
            "Game Save Loaded - Floor 2.",
            "Game Save Loaded, say restart to restart from the beginning. "
            "You are in a dimly lit corridor at the base of a ladder, ",
            jam_sound(),
            "there is something red and sticky on the floor. You can hear the clattering of metal. ",
            armour_sound(),
            "something is moving down here. "
            "You can either go forward down one corridor or move right down another. What would you like to do?",
            "Go straight ahead or right?"
        )
    elif (floor_number == 3):
        return get_audio_response(
            get_starting_floor3_attributes(),
            "What do you choose?",
            "Game Save Loaded, say restart to restart from the beginning. "
            "You are on floor 3, in a single room. "
            "You hear a noise. ",
            hatch_sound(),
            "The hole you had climbed down has been sealed from the other side. "
            "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, "
            "the other has a full victoria sponge cake. Which do you choose?",
            "Which do you choose? The cake or the doughnuts?"
        )
    else:
        return get_start_response()


def get_end_response():
    return get_audio_response(
        {},
        "Thanks for playing!",
        "Thank you for playing Mysterious House!",
        jingle_sound(),
        "",
        None,
        True
    )


def get_misunderstood_response(session_attributes):
    return get_response(
        session_attributes,
        "Sorry I don't understand what you meant by that.",
        "Sorry I don't understand what you meant by that. Try saying something else.",
        "Sorry I don't understand what you meant by that. Try saying something else."
    )


def get_error_response(error_code):
    return get_response(
        {},
        "Something has broken.",
        "Sorry something has broken, please report this issue, have a nice day. Error code " + error_code,
        None,
        True
    )

# --------------- Floor 1


def get_floor1_situation(x, visited_larry, visited_barry, session_attributes, play_door, warp_text = "", help_request = False):
    if x == 0:

        help_text = ""
        if help_request:
            help_text = "Say: Talk, to talk to barry or say: Back, to leave the room. "

        if visited_barry:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    "Barry the Ghost.",
                    "",
                    door_sound(),
                    warp_text + "Barry is still very interested in the static picture, " + help_text +
                    "Would you like to talk to Barry or head back?",
                    "Talk to Barry or go back?"
                )
            else:
                return get_response(
                    session_attributes,
                    "Barry the Ghost.",
                    warp_text + "Barry is still very interested in the static picture, " + help_text +
                    "Would you like to talk to Barry or head back?",
                    "Talk to Barry or go back?"
                )
        else:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    "Barry the Ghost.",
                    "",
                    door_sound(),
                    warp_text + "A relaxed ghost is watching a static television screen. The name plate on his desk says Barry, " +
                    help_text  + "Would you like to talk to Barry or head back?",
                    "Talk to Barry or go back?"
                )
            else:
                return get_response(
                    session_attributes,
                    "Barry the Ghost.",
                    warp_text + "A relaxed ghost is watching a static television screen. The name plate on his desk says Barry, " +
                    help_text + "Would you like to talk to Barry or head back?",
                    "Talk to Barry or go back?"
                )
    elif x == 1:

        help_text = ""
        if help_request:
            help_text = "Say: Left, to go through the left door. Say: Right, to go through the right door. "

        if play_door:
            print(warp_text)
            return get_audio_response(
                session_attributes,
                "Left or Right Door?",
                warp_text,
                 door_sound(),
                "You return back to the entrance hall. " + help_text +
                "Would you like to go through the left or right door?",
                "Left or Right door?"
            )
        elif not visited_larry and not visited_barry:
            return get_response(
                session_attributes,
                "Left or Right Door?",
                warp_text + "You have just arrived at the mysterious house, " + help_text +
                "would you like to go through the left or right door?",
                "Left or Right door?"
            )
        else:
            return get_response(
                session_attributes,
                "Left or Right Door?",
                warp_text + "You returned back to the entrance hall, " + help_text +
                "would you like to go through the left or right door?",
                "Left or Right door?"
            )
    elif x == 2:

        help_text = ""
        if help_request:
            help_text = "Say: Talk, to talk to larry or say: Back, to leave the room. "

        if visited_larry:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    "Larry the Ghost.",
                    warp_text,
                    door_sound(),
                    "Larry remains guarding the ladder, he seems a bit bored. " + help_text +
                    "Would you like to talk to Larry or head back?",
                    "Talk to Larry or go back?"
                )
            else:
                return get_response(
                    session_attributes,
                    "Larry the Ghost.",
                    warp_text + "Larry remains guarding the ladder, he seems a bit bored. " + help_text +
                    "Would you like to talk to Larry or head back?",
                    "Talk to Larry or go back?"
                )
        else:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    "Larry the Ghost.",
                    warp_text,
                    door_sound(),
                    "A ladder leading underground is guarded by a tired-looking ghost. His name tag says Larry. " +
                    help_text +
                    "There is some sort of white powder on the floor. Would you like to talk to Larry or head back?",
                    "Talk to Larry or go back?"
                )
            else:
                return get_response(
                    session_attributes,
                    "Larry the Ghost.",
                    warp_text +
                    "A ladder leading underground is guarded by a tired-looking ghost. His name tag says Larry. " +
                    help_text +
                    "There is some sort of white powder on the floor. Would you like to talk to Larry or head back?",
                    "Talk to Larry or go back?"
                )
    else:
        return get_error_response("One")


def get_barry_speech(spoken_to_barry, spoken_to_larry, visited_larry):
    if spoken_to_barry:
        return get_response(
            construct_floor1_attributes(0, True, True, True, True, False),
            "Barry Says No.",
            "Barry yells: I said no! Now get out! Would you like to talk to Barry again or go back?",
            "Barry still rejects your request, ask again or go back?"
        )
    elif spoken_to_larry:
        return get_response(
            construct_floor1_attributes(0, True, True, True, True, False),
            "Barry Says No.",
            "Barry yells: What?! You want me to let you go down a level? No chance. "
            "Would you like to talk to Barry again or go back?",
            "Barry rejects your request, ask again or go back?"
        )
    else:
        return get_response(
            construct_floor1_attributes(0, True, visited_larry, False, False, False),
            "Barry seems angry.",
            "Barry yells: You're not allowed in here, Get out! Would you like to talk to Barry again or go back?",
            "Barry doesn't want to talk, try to speak again or go back?"
        )


def get_larry_speech(spoken_to_barry, spoken_to_larry, visited_barry):
    if spoken_to_larry:
        if spoken_to_barry:
            return get_response(
                construct_floor1_attributes(2, True, True, True, True, True),
                "Larry the Ghost.",
                "Larry says: Did barry say yes?",
                "Larry asked: Did barry say yes?"
            )
        else:
            return get_response(
                construct_floor1_attributes(2, visited_barry, True, False, True, False),
                "Larry the Ghost.",
                "Larry says: Talk to barry if you want to get past. "
                "Would you like to talk to Larry again or go back?",
                "Talk to Larry again or go back?"
            )
    else:
        return get_response(
            construct_floor1_attributes(2, visited_barry, True, False, True, False),
            "Larry the Ghost.",
            "Hello I'm Larry, sorry, I can't let you continue, if you want to get past ask Barry in the other room. "
            "Would you like to talk to Larry again or go back?",
            "Talk to Larry again or go back?"
        )


# --------------- Floor 2

def get_floor2_node_info():
    # Flipped For Convenience
    return [
        [True, True, False, False, False],
        [True, True, True, True, False],
        [True, True, True, True, False],
        [True, True, False, True, True]
    ]


def get_floor2_xmax():
    return 4


def get_floor2_ymax():
    return 3


def is_at_floor2_end(x, y):
    #top right
    return  y == get_floor2_ymax() and x == get_floor2_xmax()


def get_haunted_armour_pos(x, y):
    if y == 1:
        if x == 0:
            return [0, 2]
        else:
            return [x-1, 1]
    else:
        if x == get_floor2_xmax():
            return [get_floor2_xmax(), 1]
        else:
            return [x+1, 2]


def get_floor2_directions(osstate, x, y):
    forward = False
    backward = False
    left = False
    right = False

    node_info = get_floor2_node_info()
    max_y = get_floor2_ymax()
    max_x = get_floor2_xmax()

    if osstate == 0:
        forward = True
        backward = False
        left = False
        right = True
    if osstate == 1:  # Facing North
        forward = y != max_y and node_info[y + 1][x]  # North
        backward = y != 0 and node_info[y - 1][x]  # South
        left = x != 0 and node_info[y][x - 1]  # West
        right = x != max_x and node_info[y][x + 1]  # East
    elif osstate == 2:  # Facing East
        left = y != max_y and node_info[y + 1][x]  # North
        right = y != 0 and node_info[y - 1][x]  # South
        backward = x != 0 and node_info[y][x - 1]  # West
        forward = x != max_x and node_info[y][x + 1]  # East
    elif osstate == 3:  # Facing South
        backward = y != max_y and node_info[y + 1][x]  # North
        forward = y != 0 and node_info[y - 1][x]  # South
        right = x != 0 and node_info[y][x - 1]  # West
        left = x != max_x and node_info[y][x + 1]  # East
    elif osstate == 4:  # Facing West
        right = y != max_y and node_info[y + 1][x]  # North
        left = y != 0 and node_info[y - 1][x]  # South
        forward = x != 0 and node_info[y][x - 1]  # West
        backward = x != max_x and node_info[y][x + 1]  # East

    return [forward, backward, left, right]


def get_floor2_movement_options_state(osstate, x, y):
    # Start State
    if osstate == 0:
        return ["You have just climbed down the ladder, would you like to go straight ahead? or take the path right?",
                "Go forward or right?"]

    directions = get_floor2_directions(osstate, x, y)
    forward = directions[0]
    backward = directions[1]
    left = directions[2]
    right = directions[3]

    if forward:
        if backward:
            if left:
                if right:
                    return ["You have reached a junction, would you like to go forward," \
                           " left, right or go back the way you came?", "Go forward, left, right or back?"]
                else:
                    return ["You have reached a junction, would you like to go" \
                           " forward, left, or go back the way you came?", "Go forward, left or back?"]
            elif right:
                return ["You have reached a junction, would you like to go" \
                       " forward, right, or go back the way you came?", "Go forward, right, or back?"]
            else:
                return ["You have reached a set or crates, would you like to go past or go back the way you came?",
                        "would you like to keep goingor go back?"]
        elif left:
            if right:
                return ["You have reached a junction, would you like to go straight on, left or right?",
                        "Go forward, left or right?"]
            else:
                return ["You have reached a junction, would you like to go straight on or left?",
                        "Go forward or left?"]
        elif right:
            return  ["You have reached a junction, would you like to go straight on or right?",
                     "Go forward or right?"]
        else:
            return ["You have reached a set or crates, would you like to keep going?",
                    "Would you like to keep going forward?"]
    elif backward:
        if left:
            if right:
                return ["You have reached a junction, would you like to go left, right or go back the way you came?",
                        "Go left, right or back the way you came?"]
            else:
                return ["The path bends suddenly to the left, " \
                       "would you like to follow the path left or go back the way you came?",
                        "would you like to follow the path left or go back the way you came?"]
        elif right:
            return ["The path bends suddenly to the right, " \
                    "would you like to follow the path right or go back the way you came?",
                    "would you like to follow the path right or go back the way you came?"]
        else:
            return ["You have reached a dead end, would you like to go back the way you came?",
                    "A dead end, would you like to go back the way you came?"]
    elif left:
        if right:
            return ["You have reached a junction, would you like to go left or right?",
                    "Go left or right?"]
        else:
            return ["The path bends suddenly to the left, would you like to follow the path?",
                    "Would you like to follow the path to the left?"]
    elif right:
        return ["The path bends suddenly to the right, would you like to follow the path?",
                "Would you like to follow the path to the right?"]


def get_move_response(osstate, x, y, flavour_text, mob_x, mob_y, userId):

    # Find New Armour Pos
    haunted_armour_pos = get_haunted_armour_pos(mob_x, mob_y)
    mob_x = haunted_armour_pos[0];
    mob_y = haunted_armour_pos[1];

    # Mob Detection
    if (x == mob_x and y == mob_y):
        return get_audio_response(
            get_starting_floor2_attributes(),
            "You got caught!",
            flavour_text + " Suddenly A haunted suit of armour looms from the shadows. ",
            armour_sound(),
            "You black out. "
            "You awake at the base of the ladder. Would you like to go straight ahead or right?",
            "Go straight ahead of right?"
        )

    # End Detection
    elif is_at_floor2_end(x, y):
        SaveFloorNumber(userId, 3)
        return  get_audio_response(
            get_starting_floor3_attributes(),
            "What do you choose?",
            flavour_text + "You found another ladder, going down another level deeper. "
            "You climb down and end up in a single room. "
            "You hear a noise. ",
            hatch_sound(),
            "The hole you just climbed down has been sealed from the other side. "
            "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, "
            "the other has a full victoria sponge cake. Which do you choose?",
            "Which do you choose? The doughnuts or the cake?"
        )

    # Normal Update
    else:
        movement_options = get_floor2_movement_options_state(osstate, x, y)
        return get_response(
            construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
            "Where to move?",
            flavour_text + movement_options[0],
            movement_options[1]
        )


def get_move_forward_response(osstate, x, y, mob_x, mob_y, userId):
        if osstate <= 1: # north
            y+=1
        elif osstate == 2: # east
            x+=1
        elif osstate == 3: # south
            y-=1
        elif osstate == 4: # west
            x-=1
        else:
            return  get_error_response("Two")
        return get_move_response(osstate, x, y, "You continue straight ahead. ", mob_x, mob_y, userId)


def get_move_backward_response(osstate, x, y, mob_x, mob_y, userId):
        directions = get_floor2_directions(osstate, x, y)
        if osstate <= 1:  # south
            y -= 1
            osstate = 3
        elif osstate == 2:  # west
            x -= 1
            osstate = 4
        elif osstate == 3:  # north
            y += 1
            osstate = 1
        elif osstate == 4:  # east
            x += 1
            osstate = 2
        else:
            return get_error_response("Three")
        return get_move_response(osstate, x, y, "You turn around and go back. ", mob_x, mob_y, userId)


def get_move_left_response(osstate, x, y, is_continue, mob_x, mob_y, userId):
        directions = get_floor2_directions(osstate, x, y)
        if osstate <= 1:  # west
            x -= 1
            osstate = 4
        elif osstate == 2:  # north
            y += 1
            osstate = 1
        elif osstate == 3:  # east
            x += 1
            osstate = 2
        elif osstate == 4:  # south
            y -= 1
            osstate = 3
        else:
            return get_error_response("Four")

        flavour_text = ""
        if is_continue:
            flavour_text = "You follow the path left. "
        else:
            flavour_text = "You turn left. "
        return get_move_response(osstate, x, y, flavour_text, mob_x, mob_y, userId)


def get_move_right_response(osstate, x, y, is_continue, mob_x, mob_y, userId):
        if osstate <= 1:  # east
            x += 1
            osstate = 2
        elif osstate == 2:  # south
            y -= 1
            osstate = 3
        elif osstate == 3:  # west
            x -= 1
            osstate = 4
        elif osstate == 4:  # north
            y += 1
            osstate = 1
        else:
            return get_error_response("Five")

        flavour_text = ""
        if is_continue:
            flavour_text = "You follow the path right. "
        else:
            flavour_text = "You turn right. "
        return get_move_response(osstate, x, y, flavour_text, mob_x, mob_y, userId)

# --------------- Events ------------------


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    return get_start_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    userId = session['user']['userId']
    warp_response = ""

    # Deal with stops and start overs
    if intent_name == "AMAZON.StopIntent" or intent_name == "AMAZON.CancelIntent":
        return get_end_response()
    elif intent_name == "AMAZON.StartOverIntent":
        return get_start_response()
    elif intent_name == "WarpIntent":
        [warp_error, warp_response] = on_intent_warp(intent, session, userId)
        if (warp_error == False):
            return warp_response

    # Get Floor
    floor = get_floor_number(session)
    # Select correct event based on floor
    if floor == 1:
        return on_intent_floor1(intent_name, session, userId, warp_response)
    elif floor == 2:
        return on_intent_floor2(intent_name, session, userId, warp_response)
    elif floor == 3:
        return on_intent_floor3(intent_name, session, userId, warp_response)
    else:
        return initial_load_response(userId)

def on_intent_warp(intent, session, userId):
    isError = False
    response = ""

    if (LoadCanWarp(userId)):
        if intent.get('slots', {}) and "floor" in intent.get('slots', {}) and "value" in intent['slots']['floor']:
            floor_number = intent['slots']['floor']['value']
            if (floor_number == '1'):
                response = get_start_response()
            elif (floor_number == '2'):
                response = get_doubleaudio_response(
                    get_starting_floor2_attributes(),
                    "Warp to floor 2.",
                    "You warp to a dimly lit corridor at the base of a ladder, ",
                    jam_sound(),
                    "there is something red and sticky on the floor. You can hear the clattering of metal. ",
                    armour_sound(),
                    "something is moving down here. "
                    "You can either go forward down one corridor or move right down another. What would you like to do?",
                    "Go straight ahead or right?"
                )
            elif (floor_number == '3'):
                response = get_audio_response(
                    get_starting_floor3_attributes(),
                    "What do you choose?",
                    "You warp to floor 3 and end up in a single room. "
                    "You hear a noise. ",
                    hatch_sound(),
                    "The hole you just climbed down has been sealed from the other side. "
                    "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, "
                    "the other has a full victoria sponge cake. Which do you choose?",
                    "Which do you choose? The cake or the doughnuts?"
                )
            elif session.get('attributes', {}) and "Floor" in session.get('attributes', {}):
                isError = True
                response = 'That floor does not exist, you can only warp to floors one, two and three. '
            else:
                response = get_start_response()
        elif session.get('attributes', {}) and "Floor" in session.get('attributes', {}):
            isError = True
            response = 'You cannot warp to that floor. '
    else:
        if session.get('attributes', {}) and "Floor" in session.get('attributes', {}):
            isError = True
            response = 'You have not unlocked warping yet. '
        else:
            response = get_start_response()

    return [isError, response]


def on_intent_floor1(intent_name, session, userId, warp_text):
    # Get Values and Check validity
    x = get_x(session)
    if x == -1:
        return get_error_response("Seven")

    visited_larry = get_visited_larry(session)
    if visited_larry == -1:
        return get_error_response("Eight")

    visited_barry = get_visited_barry(session)
    if visited_barry == -1:
        return get_error_response("Nine")

    spoken_to_larry = get_spoken_to_larry(session)
    if spoken_to_larry == -1:
        return get_error_response("Ten")

    spoken_to_barry = get_spoken_to_barry(session)
    if spoken_to_barry == -1:
        return get_error_response("Eleven")

    asking_larry = get_larry_asking(session)
    if asking_larry == -1:
        return get_error_response("Twelve")

    # Intent Processing

    if intent_name == "AMAZON.HelpIntent" or intent_name == "AMAZON.RepeatIntent" or intent_name == "PlayIntent" or intent_name == "WarpIntent":
        return  get_floor1_situation(x, visited_larry, visited_barry,
                                     construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                                                    spoken_to_larry, asking_larry), False,
                                     warp_text, intent_name == "AMAZON.HelpIntent"
                                     )
    elif intent_name == "LeftIntent":
        # Move to left room when in entrance hall
        if x == 1:
            return get_floor1_situation(0, visited_larry, visited_barry,
                                        construct_floor1_attributes(0, True, visited_larry, spoken_to_barry,
                                                                    spoken_to_larry, asking_larry), True, ""
                                        )
        elif x == 0:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action.",
                "You can't go left here.",
                "Talk to Barry or go back?"
            )
        else:
            return  get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action.",
                "You can't go left here.",
                "Talk to Larry or go back?"
            )
    elif intent_name == "RightIntent":
        # Move to right room when in entrance hall
        if x == 1:
            return get_floor1_situation(2, visited_larry, visited_barry,
                                        construct_floor1_attributes(2, visited_barry, True, spoken_to_barry,
                                                                    spoken_to_larry, asking_larry), True, ""
                                        )
        elif x == 0:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action.",
                "You can't go right here.",
                "Talk to Barry or go back?"
            )
        else:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action.",
                "You can't go right here.",
                "Talk to Larry or go back?"
            )
    elif intent_name == "BackwardIntent" or intent_name == "FirstFloorBackwardIntent":
        # Move back to the entrance hall
        if x == 0 or x == 2:
            return get_floor1_situation(1, visited_larry, visited_barry,
                                        construct_floor1_attributes(1, visited_barry, visited_larry, spoken_to_barry,
                                                                    spoken_to_larry, asking_larry), True, ""
                                        )
        else:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action.",
                "You are in the entrance hall, there is no escaping.",
                "Go left or right?"
            )
    elif intent_name == "TalkIntent":
        if x == 0:
            return get_barry_speech(spoken_to_barry, spoken_to_larry, visited_larry)
        elif x == 2:
            return  get_larry_speech(spoken_to_barry, spoken_to_larry, visited_barry)
        else:
            return  get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action",
                "There is nobody to speak to here.",
                "Go left or right?"
            )
    elif intent_name == "TalkToLarryIntent":
        if x == 2:
            return get_larry_speech(spoken_to_barry, spoken_to_larry, visited_barry)
        elif x == 1:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action",
                "Larry isn't here.",
                "Go left or right?"
            )
        else:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action",
                "Larry isn't here.",
                "Talk to Barry or Go Back?"
            )
    elif intent_name == "TalkToBarryIntent":
        if x == 0:
            return get_barry_speech(spoken_to_barry, spoken_to_larry, visited_larry)
        elif x == 1:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action",
                "Barry isn't here.",
                "Go left or right?"
            )
        else:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                "Invalid Action",
                "Barry isn't here.",
                "Talk to Larry or Go Back?"
            )
    elif intent_name == "AMAZON.NoIntent" or intent_name == "BarrySaidNoIntent":
        if asking_larry:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, False,
                                            spoken_to_larry, False),
                "Larry the Ghost.",
                "Larry Says: Oh Too bad, sorry I can't let you go.",
                "Talk to Larry again or go back?"
            )
        else:
            return get_misunderstood_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry))
    elif intent_name == "AMAZON.YesIntent" or intent_name == "BarrySaidYesIntent":
        if asking_larry:
            SaveFloorNumber(userId, 2)
            return get_doubleaudio_response(
                get_starting_floor2_attributes(),
                "Down the Ladder.",
                "Larry seems surprised but lets you climb down the ladder anyway. "
                "The ladder stops in a dimly lit corridor. ",
                jam_sound(),
                "There is something red and sticky on the floor. "
                "You can hear the clattering of metal. ",
                armour_sound(),
                "Something is moving down here. "
                "You can either go forward down one corridor or move right down another. What would you like to do?",
                "Go forward or go right?"
            )
        else:
            return get_misunderstood_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry))

    return get_misunderstood_response(
        construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                    spoken_to_larry, asking_larry))


def on_intent_floor2(intent_name, session, userId, warp_text):
    # Get values and validate
    x = get_x(session)
    if x == -1:
        return get_error_response("A")

    y = get_y(session)
    if y == -1:
        return get_error_response("B")

    osstate = get_ostate(session)
    if osstate == -1:
        return get_error_response("C")

    mob_x = get_mob_x(session)
    if mob_x == -1:
        return get_error_response("D")

    mob_y = get_mob_y(session)
    if mob_y == -1:
        return get_error_response("E")

    # Move Tracker
    player_moved = False

    # Handle Intent
    if intent_name == "AMAZON.RepeatIntent" or intent_name == "PlayIntent" or intent_name == "WarpIntent":
        movement_options = get_floor2_movement_options_state(osstate, x, y)
        return get_response(
            construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
            "How do you want to move?",
            warp_text + movement_options[0],
            movement_options[1]
        )
    elif intent_name == "AMAZON.HelpIntent":
        movement_options = get_floor2_movement_options_state(osstate, x, y)
        return get_response(
            construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
            "How do you want to move?",
            "On this floor you can move the character. Say: forward, to move the direction the character is facing. "
            "Say: left, to turn left. Say: right, to turn right, Say: back, to turn around "
            "and go back to where you came from. " + movement_options[0],
            movement_options[1]
        )
    elif intent_name == "ForwardIntent":
        directions = get_floor2_directions(osstate, x, y)
        if directions[0]:
            return get_move_forward_response(osstate, x, y, mob_x, mob_y, userId)
        else:
            movement_options = get_floor2_movement_options_state(osstate, x, y)
            return get_response(
                construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
                "Invalid Action",
                "You cannot move forward here.",
                movement_options[1]
            )
    elif intent_name == "BackwardIntent":
        directions = get_floor2_directions(osstate, x, y)
        if directions[1]:
            return get_move_backward_response(osstate, x, y, mob_x, mob_y, userId)
        else:
            movement_options = get_floor2_movement_options_state(osstate, x, y)
            return get_response(
                construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
                "Invalid Action",
                "There is no escape.",
                movement_options[1]
            )
    elif intent_name == "LeftIntent" or intent_name == "ContinueLeftIntent":
        directions = get_floor2_directions(osstate, x, y)
        if directions[2]:
            return get_move_left_response(osstate, x, y, intent_name == "ContinueLeftIntent", mob_x, mob_y, userId)
        else:
            movement_options = get_floor2_movement_options_state(osstate, x, y)
            return get_response(
                construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
                "Invalid Action",
                "You cannot move left here.",
                movement_options[1]
            )
    elif intent_name == "RightIntent" or intent_name == "ContinueRightIntent":
        directions = get_floor2_directions(osstate, x, y)
        if directions[3]:
            return  get_move_right_response(osstate, x, y, intent_name == "ContinueRightIntent", mob_x, mob_y, userId)
        else:
            movement_options = get_floor2_movement_options_state(osstate, x, y)
            return  get_response(
                construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
                "Invalid Action",
                "You cannot move right here.",
                movement_options[1]
            )
    elif intent_name == "ContinueIntent":
        directions = get_floor2_directions(osstate, x, y)
        # Right Only (except back)
        if (not directions[0]) and (not directions[2]) and directions[3]:
            return get_move_right_response(osstate, x, y, True, mob_x, mob_y, userId)

        # Left Only (except back)
        elif (not directions[0]) and directions[2] and (not directions[3]):
            return get_move_left_response(osstate, x, y, True, mob_x, mob_y, userId)

        # Forward
        elif (directions[0]):
            return get_move_forward_response(osstate, x, y, mob_x, mob_y, userId)
        else:
            movement_options = get_floor2_movement_options_state(osstate, x, y)
            return get_response(
                construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
                "Invalid Action",
                "You can't continue forward here.",
                movement_options[1]
            )
    return get_misunderstood_response(
        construct_floor2_attributes(x, y, osstate, mob_x, mob_y))


def on_intent_floor3(intent_name, session, userId, warp_text):
    # No attributes just intent checks
    if intent_name == "AMAZON.RepeatIntent" or intent_name == "PlayIntent" or intent_name == "WarpIntent":
        return get_response(
            get_starting_floor3_attributes(),
            "What do you choose?",
            warp_text +
            "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, "
            "the other has a full victoria sponge cake. Which do you choose?",
            "Which do you choose? The cake or the doughnuts?"
        )
    elif intent_name == "AMAZON.HelpIntent":
        return get_response(
            get_starting_floor3_attributes(),
            "What do you choose?",
            "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, "
            "the other has a full victoria sponge cake. To choose the cake, Say: Cake. To choose the doughnuts, "
            "Say: Doughnuts. Do you choose the cake or the doughnuts?",
            "Which do you choose? The cake or the doughnuts?"
        )
    # Cake
    elif intent_name == "CakeIntent":
        SaveAll(userId, True, 1)
        return get_audio_response(
            {},
            "You ate the cake.",
            "You take a slice of victoria sponge cake. It's the most delicious cake you've ever eaten. "
            "Suddenly you start coughing violently. You have been poisoned. "
            "You turn around to find a haunted suit of armour. He says: I'm free thank you. "
            "The spirit possessing the armour, leaves the suit and fades away into nothingness. You black out. "
            "You awake to find you have no body, you are a spirit possessing the same suit of armour, "
            "doomed to walk these halls forever. The End. On future replays you can say, warp to floor X, to replay any part you like. Thank you for playing!",
            jingle_sound(),
            "",
            None,
            True # End Game Here
        )
    elif intent_name == "DoughnutIntent":
        SaveAll(userId, True, 1)
        return get_audio_response(
            {},
            "You ate the doughnuts.",
            "You start eating the doughnuts. The insides ooze with a flavour you've never tasted before. "
            "They are the most delicious doughnuts you've ever eaten, you get a sudden pain in the stomach. "
            "You have been poisoned. You look back to find a familiar face. It's Larry. He says: Thank you, "
            "I can now move on. He fades away into nothingness. You black out. "
            "You awake at the top of the first ladder, you look down at yourself, you're transparent and floating, "
            "You are wearing a nametag, it says Larry. The End. On future replays you can say, warp to floor X, to replay any part you like. Thank you for playing!",
            jingle_sound(),
            "",
            None,
            True  # End Game Here
        )
    elif intent_name == "BothTreatsIntent":
        SaveAll(userId, True, 1)
        return get_audio_response(
            {},
            "You ate both the doughnuts and the cake.",
            "You eat a doughnut. You get a sudden pain in the stomach. You quickly take a bite of cake.  "
            "The pain stopped as suddenly as it started. "
            "You look back to find a familiar face. It's Barry. He laughs and says, fool, they were poisoned and now "
            "you'll be my prisoner. Both you and Barry wait for an awkward ammount of time. I don't understand, exclaimed "
            "Barry, the poison in both foods must cancel each other out. You and Barry stare at each other for a while. "
            "Barry can't trick you into taking poison, and you can't attack a ghost. You leave the mysterious house. You "
            "solved the mystery and survived, leaving an irked Barry behind. "
            "The End. On future replays you can say, warp to floor X, to replay any part you like. Thank you for playing!",
            jingle_sound(),
            "",
            None,
            True  # End Game Here
        )
    else:
        return get_response(
            get_starting_floor3_attributes(),
            "What do you choose?",
            "I'm sorry I didn't understand that, do you want the cake or the doughnuts?",
            "Which do you choose? The cake or the doughnuts?"
        )
    return get_misunderstood_response(get_starting_floor3_attributes())


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
             "amzn1.ask.skill.499ef157-c8f7-455f-b547-257916c78946"):
         raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    boto3.setup_default_session(region_name='eu-west-1')

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
