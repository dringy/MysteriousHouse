# -*- coding: utf-8 -*-
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
            UpdateExpression="set CanWarp=:c, FloorNumber=:f, LastUpdate=:u",
            ExpressionAttributeValues={
                ':c': LoadCanWarp(userID),
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
            UpdateExpression="set CanWarp=:c, FloorNumber=:f, LastUpdate=:u",
            ExpressionAttributeValues={
                ':c': canWarp,
                ':f': LoadFloorNumber(userID),
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

# --------------- Locale

def locale_de():
    return locale == "de-DE"

# --------------- Text Body

def Speech_Start_1():
    if locale_de():
        return "Du kommst zu einem geheimnisvollen Haus und öffnest die Eingangstür. "
    else:
        return "You arrive at a mysterious house and open the front door. "

def Speech_Start_2():
    if locale_de():
        return "Du siehst zwei weitere Türen – eine nach links und eine nach rechts. Welche Tür möchtest du zuerst öffnen? "
    else:
        return "You see two more doors, one left and one right. Which door would you like to open first? "

def Speech_Start_repeat():
    if locale_de():
        return "Die linke oder die rechte Tür öffnen? "
    else:
        return "Open the left or right door? "

def Speech_Load_Floor2_1():
    if locale_de():
        return "Gespeichertes Spiel geladen, sage „Neustart“, um erneut zu beginnen. Du befindest dich in einem schwach beleuchteten Korridor am unteren Ende einer Leiter. "
    else:
        return "Game Save Loaded, say restart to restart from the beginning. You are in a dimly lit corridor at the base of a ladder. "

def Speech_Load_Floor2_2():
    if locale_de():
        return "Auf dem Boden ist etwas Rotes, Klebriges. Du hörst das Geräusch von Metall auf Metall. "
    else:
        return "There is something red and sticky on the floor. You can hear the clattering of metal. "

def Speech_Load_Floor2_3():
    if locale_de():
        return "Etwas bewegt sich hier unten. Du kannst entweder vorwärts einen Korridor hinunter oder nach rechts " \
               "in einen anderen Korridor gehen. Was möchtest du tun? "
    else:
        return "something is moving down here. You can either go forward down one corridor or move right " \
               "down another. What would you like to do? "

def Speech_Load_Floor2_repeat():
    if locale_de():
        return "Geradeaus oder nach rechts gehen? "
    else:
        return "Go straight ahead or right? "

def Speech_Load_Floor3_1():
    if locale_de():
        return "Gespeichertes Spiel geladen, sage „Neustart“, um erneut zu beginnen. Du bist auf Etage 3, in " \
               "einem einzelnen Raum. Du hörst ein Geräusch. "
    else:
        return "Game Save Loaded, say restart to restart from the beginning. You are on floor 3, in a single room. " \
               "You hear a noise. "

def Speech_Load_Floor3_2():
    if locale_de():
        return "Das Loch, in das du hinabgestiegen bist, wurde von der anderen Seite verschlossen. " \
               "Vor dir siehst du zwei leckere Sachen auf kleinen Holztischen, " \
               "einen Teller mit glasierten Donuts und auf dem anderen Tisch einen Biskuitkuchen. " \
               "Wofür entscheidest du dich? "
    else:
        return "The hole you had climbed down has been sealed from the other side. " \
               "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, " \
               "the other has a full Victoria sponge cake. Which do you choose? Which do you choose? "

def Speech_Load_Floor3_repeat():
    if locale_de():
        return "Wofür entscheidest du dich? Nimmst du den Kuchen oder die Donuts? "
    else:
        return "Which do you choose? The cake or the doughnuts? "

def Speech_End():
    if locale_de():
        return "Viele Dank dafür, dass du Mysterious House spielst! "
    else:
        return "Thank you for playing Mysterious House! "

def Speech_misunderstood():
    if locale_de():
        return "Ich habe leider nicht verstanden, was du damit meinst. Bitte sage etwas anderes. "
    else:
        return "Sorry I don't understand what you meant by that. Try saying something else. "

def Speech_error(error_code):
    if locale_de():
        return "Leider ist etwas nicht in Ordnung, bitte melde den Vorfall, einen schönen Tag noch. " \
               "Fehlercode " + error_code
    else:
        return "Sorry something has broken, please report this issue, have a nice day. Error code " + error_code

def Speech_Floor1_X0_Help():
    if locale_de():
        return "Sage: „Sprechen“, um zu Barry zu sprechen, oder „Zurück“, um den Raum zu verlassen. "
    else:
        return "Say: Talk, to talk to Barry or say: Back, to leave the room. "

def Speech_Floor1_X0_Revisit_1():
    if locale_de():
        return "Barry ist immer noch sehr an dem statischen Bild interessiert, "
    else:
        return "Barry is still very interested in the static picture, "

def Speech_Floor1_X0_Revisit_2():
    if locale_de():
        return "Möchtest du zu Barry sprechen oder zurückgehen? "
    else:
        return "Would you like to talk to Barry or head back? "

def Speech_Floor1_X0_Visit_1():
    if locale_de():
        return "Ein entspannter Geist betrachtet einen statischen Fernsehbildschirm. Auf dem Namensschild auf seinem Tisch steht „Barry“. "
    else:
        return "A relaxed ghost is watching a static television screen. The name plate on his desk says Barry. "

def Speech_Floor1_X0_Visit_2():
    if locale_de():
        return "Möchtest du zu Barry sprechen oder zurückgehen? "
    else:
        return "Would you like to talk to Barry or head back? "

def Speech_Floor1_X0_Visit_Rep():
    if locale_de():
        return "Zu Barry sprechen oder zurückgehen? "
    else:
        return "Talk to Barry or go back? "

def Speech_Floor1_X1_Help():
    if locale_de():
        return "Sage: „Links“, um durch die linke Tür zu gehen. Sage: „Rechts“, um durch die rechte Tür zu gehen. "
    else:
        return "Say: Left, to go through the left door. Say: Right, to go through the right door. "

def Speech_Floor1_X1_Revisit_1():
    if locale_de():
        return "Du gelangst zur Eingangshalle zurück. "
    else:
        return "You return back to the entrance hall. "

def Speech_Floor1_X1_Revisit_2():
    if locale_de():
        return "Möchtest du durch die linke oder durch die rechte Tür gehen? "
    else:
        return "Would you like to go through the left or right door? "

def Speech_Floor1_X1_Visit_1():
    if locale_de():
        return "Du bist gerade an dem geheimnisvollen Haus angekommen. "
    else:
        return "You have just arrived at the mysterious house, "

def Speech_Floor1_X1_Visit_2():
    if locale_de():
        return "Möchtest du durch die linke oder durch die rechte Tür gehen? "
    else:
        return "would you like to go through the left or right door? "

def Speech_Floor1_X1_Visit_Rep():
    if locale_de():
        return "Linke oder rechte Tür? "
    else:
        return "Left or Right door? "

def Speech_Floor1_X2_Help():
    if locale_de():
        return "Sage: „Sprechen“, um zu Larry zu sprechen, oder „Zurück“, um den Raum zu verlassen. "
    else:
        return "Say: Talk, to talk to Larry or say: Back, to leave the room. "

def Speech_Floor1_X2_Revisit_1():
    if locale_de():
        return "Larry bewacht weiterhin die Leiter, er sieht etwas gelangweilt aus. "
    else:
        return "Larry remains guarding the ladder, he seems a bit bored. "

def Speech_Floor1_X2_Revisit_2():
    if locale_de():
        return "Möchtest du zu Larry sprechen oder zurückgehen? "
    else:
        return "Would you like to talk to Larry or head back? "

def Speech_Floor1_X2_Visit_1():
    if locale_de():
        return "Eine nach unten führende Leiter wird von einem müde aussehenden Geist bewacht. " \
               "Auf seinem Namensschild steht „Larry“"
    else:
        return "A ladder leading underground is guarded by a tired-looking ghost. His name tag says Larry. "

def Speech_Floor1_X2_Visit_2():
    if locale_de():
        return "Auf dem Boden befindet sich eine Art weißes Pulver. Möchtest du zu Larry sprechen oder zurückgehen?"
    else:
        return "There is some sort of white powder on the floor. Would you like to talk to Larry or head back? "

def Speech_Floor1_X2_Visit_Rep():
    if locale_de():
        return "Zu Larry sprechen oder zurückgehen? "
    else:
        return "Talk to Larry or go back? "

def Speech_Floor1_BarryInitial():
    if locale_de():
        return "Barry ruft: Du hast hier nichts zu suchen, raus! Möchtest du erneut zu Barry sprechen oder " \
               "zurückgehen? "
    else:
        return "Barry yells: You're not allowed in here, Get out! Would you like to talk to Barry again or go back? "

def Speech_Floor1_BarryAsk():
    if locale_de():
        return "Barry ruft: Was?! Ich soll eine Ebene hinab gehen? Kommt nicht in Frage. " \
               "Möchtest du erneut zu Barry sprechen oder zurückgehen? "
    else:
        return "Barry yells: What?! You want me to let you go down a level? No chance. " \
               "Would you like to talk to Barry again or go back? "

def Speech_Floor1_BarryAsk_Revisit():
    if locale_de():
        return "Barry ruft: Ich sagte „Nein“! Und jetzt raus! Möchtest du erneut zu Barry sprechen oder zurückgehen? "
    else:
        return "Barry yells: I said no! Now get out! Would you like to talk to Barry again or go back? "

def Speech_Floor1_BarryInitial_Repeat():
    if locale_de():
        return "Barry möchte nicht reden, möchtest du erneut versuchen, zu ihm zu sprechen, oder gehst du zurück? "
    else:
        return "Barry doesn't want to talk, try to speak again or go back? "

def Speech_Floor1_BarryAsk_Repeat():
    if locale_de():
        return "Barry lehnt deine Bitte ab, erneut fragen oder zurück gehen? "
    else:
        return "Barry rejects your request, ask again or go back? "

def Speech_Floor1_BarryAsk_Revisit_Repeat():
    if locale_de():
        return "Barry lehnt deine Bitte immer noch ab, erneut fragen oder zurück gehen? "
    else:
        return "Barry still rejects your request, ask again or go back? "

def Speech_Floor1_Larry():
    if locale_de():
        return "Hallo, ich heiße Larry. Ich kann dich nicht weiter lassen. Wenn du weiter willst, " \
               "frage Barry im anderen Raum. Möchtest du erneut zu Larry sprechen oder zurückgehen?"
    else:
        return "Hello I'm Larry, sorry, I can't let you continue, " \
               "if you want to get past ask Barry in the other room. Would you like to talk to Larry again or go back?"

def Speech_Floor1_Larry_Revisit():
    if locale_de():
        return "Larry sagt: Sprich mit Barry, wenn du weiter willst. "
    else:
        return "Larry says: Talk to Barry if you want to get past. "

def Speech_Floor1_Larry_PostBarry():
    if locale_de():
        return "Larry sagt: Hat Barry „Ja“ gesagt? "
    else:
        return "Larry says: Did Barry say yes? "

def Speech_Floor1_Larry_Repeat():
    if locale_de():
        return "Erneut zu Larry sprechen oder zurückgehen? "
    else:
        return "Talk to Larry again or go back? "

def Speech_Floor2_Start():
    if locale_de():
        return "Du bist gerade die Leiter hinuntergeklettert, möchtest du geradeaus gehen? " \
               "Oder möchtest du den Weg nach rechts nehmen? "
    else:
        return "You have just climbed down the ladder, would you like to go straight ahead? or take the path right? "

def Speech_Floor2_Start_Repeat():
    if locale_de():
        return "Vorwärts oder nach rechts? "
    else:
        return "Go forward or right? "

def Speech_Floor2_FLRB():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du vorwärts, nach links, nach rechts oder wieder zurück " \
               "gehen? "
    else:
        return "You have reached a junction, would you like to go forward, left, right or go back the way you came? "

def Speech_Floor2_FLRB_Repeat():
    if locale_de():
        return "Vorwärts, nach links, nach rechts, oder zurück? "
    else:
        return "Go forward, left, right or back? "

def Speech_Floor2_FLR():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du geradeaus, nach links oder nach rechts gehen? "
    else:
        return "You have reached a junction, would you like to go straight on, left or right? "

def Speech_Floor2_FLR_Repeat():
    if locale_de():
        return "Vorwärts, nach links oder nach rechts? "
    else:
        return "Go forward, left or right? "

def Speech_Floor2_FLB():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du vorwärts, nach links oder wieder zurück gehen? "
    else:
        return "You have reached a junction, would you like to go forward, left, or go back the way you came? "

def Speech_Floor2_FLB_Repeat():
    if locale_de():
        return "Vorwärts, nach links oder zurück? "
    else:
        return "Go forward, left or back? "

def Speech_Floor2_FRB():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du vorwärts, nach rechts oder wieder zurück gehen? "
    else:
        return "You have reached a junction, would you like to go forward, right, or go back the way you came? "

def Speech_Floor2_FRB_Repeat():
    if locale_de():
        return "Vorwärts, nach rechts oder zurück? "
    else:
        return "Go forward, right, or back? "

def Speech_Floor2_LRB():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du nach links, nach rechts oder wieder zurück gehen? "
    else:
        return "You have reached a junction, would you like to go left, right or go back the way you came? "

def Speech_Floor2_LRB_Repeat():
    if locale_de():
        return "Nach links, nach rechts oder wieder zurück? "
    else:
        return "Go left, right or back the way you came? "

def Speech_Floor2_FL():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du geradeaus oder nach links gehen? "
    else:
        return "You have reached a junction, would you like to go straight on or left? "

def Speech_Floor2_FL_Repeat():
    if locale_de():
        return "Vorwärts oder nach links? "
    else:
        return "Go forward or left? "

def Speech_Floor2_FR():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du geradeaus oder nach rechts gehen? "
    else:
        return "You have reached a junction, would you like to go straight on or right? "

def Speech_Floor2_FR_Repeat():
    if locale_de():
        return "Vorwärts oder nach rechts? "
    else:
        return "Go forward or right? "

def Speech_Floor2_LR():
    if locale_de():
        return "Du hast eine Kreuzung erreicht, möchtest du nach links, nach rechts oder wieder zurück gehen? "
    else:
        return "You have reached a junction, would you like to go left, right or go back the way you came? "

def Speech_Floor2_LR_Repeat():
    if locale_de():
        return "Nach links, nach rechts oder wieder zurück? "
    else:
        return "Go left, right or back the way you came? "

def Speech_Floor2_LB():
    if locale_de():
        return "Der Weg knickt plötzlich nach links ab, " \
               "möchtest du ihm weiter nach links folgen oder wieder zurück gehen? "
    else:
        return "The path bends suddenly to the left, " \
               "would you like to follow the path left or go back the way you came? "

def Speech_Floor2_LB_Repeat():
    if locale_de():
        return "möchtest du dem Pfad nach links folgen oder wieder zurück gehen? "
    else:
        return "would you like to follow the path left or go back the way you came? "

def Speech_Floor2_RB():
    if locale_de():
        return "Der Weg knickt plötzlich nach rechts ab, " \
               "möchtest du ihm weiter nach rechts folgen oder wieder zurück gehen? "
    else:
        return "The path bends suddenly to the right, " \
               "would you like to follow the path right or go back the way you came? "

def Speech_Floor2_RB_Repeat():
    if locale_de():
        return "möchtest du dem Pfad nach rechts folgen oder wieder zurück gehen? "
    else:
        return "would you like to follow the path right or go back the way you came? "

def Speech_Floor2_Armour_1():
    if locale_de():
        return " Plötzlich tritt eine Geisterritterrüstung aus dem Schatten. "
    else:
        return " Suddenly A haunted suit of armour looms from the shadows. "

def Speech_Floor2_Armour_2():
    if locale_de():
        return "Du fällst in Ohnmacht. Die erwachst am Fuße einer Leiter. " \
               "Möchtest du geradeaus oder nach rechts gehen?"
    else:
        return "You black out. You awake at the base of the ladder. " \
               "Would you like to go straight ahead or right? "

def Speech_Floor2_Armour_Repeat():
    if locale_de():
        return "Geradeaus oder nach rechts? "
    else:
        return "Go straight ahead of right? "

def Speech_Floor2_End_1():
    if locale_de():
        return " Die findest eine weitere Leiter, die eine weitere Ebene nach unten führt. " \
               "Du kletterst hinunter und gelangst in einen einzelnen Raum. Du hörst ein Geräusch. "
    else:
        return " You found another ladder, going down another level deeper. " \
               "You climb down and end up in a single room. You hear a noise.  "

def Speech_Floor2_End_2():
    if locale_de():
        return " Das Loch, in das du gerade hinabgestiegen bist, wurde von der anderen Seite verschlossen. " \
               "Vor dir siehst du zwei leckere Sachen auf kleinen Holztischen, " \
               "einen Teller mit glasierten Donuts und auf dem anderen Tisch einen Biskuitkuchen. " \
               "Wofür entscheidest du dich? "
    else:
        return " The hole you just climbed down has been sealed from the other side. " \
               "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, " \
               "the other has a full Victoria sponge cake. Which do you choose? "

def Speech_Floor2_End_Repeat():
    if locale_de():
        return "Wofür entscheidest du dich? Nimmst du die Donuts oder den Kuchen? "
    else:
        return "Which do you choose? The doughnuts or the cake? "

def Speech_Floor2_Action_F():
    if locale_de():
        return "Du gehst weiter geradeaus. "
    else:
        return "You continue straight ahead. "

def Speech_Floor2_Action_B():
    if locale_de():
        return "Du drehst dich um und gehst zurück. "
    else:
        return "You turn around and go back. "

def Speech_Floor2_Action_L():
    if locale_de():
        return "Du wendest dich nach links. "
    else:
        return "You turn left. "

def Speech_Floor2_Action_LF():
    if locale_de():
        return "Du folgst dem Pfad nach links. "
    else:
        return "You follow the path left. "

def Speech_Floor2_Action_R():
    if locale_de():
        return "Du wendest dich nach rechts. "
    else:
        return "You turn right. "

def Speech_Floor2_Action_RF():
    if locale_de():
        return "Du folgst dem Pfad nach rechts. "
    else:
        return "You follow the path right. "

def Speech_Warp2_1():
    if locale_de():
        return "Du springst in einen schwach beleuchteten Korridor am unteren Ende einer Leiter, "
    else:
        return "You warp to a dimly lit corridor at the base of a ladder, "

def Speech_Warp2_2():
    if locale_de():
        return "Auf dem Boden ist etwas Rotes, Klebriges. Du hörst das Geräusch von Metall auf Metall. "
    else:
        return "There is something red and sticky on the floor. You can hear the clattering of metal. "

def Speech_Warp2_3():
    if locale_de():
        return "Etwas bewegt sich hier unten. Du kannst entweder vorwärts einen Korridor hinunter " \
               "oder nach rechts in einen anderen Korridor gehen. Was möchtest du tun? "
    else:
        return "Something is moving down here. " \
               "You can either go forward down one corridor or move right down another. What would you like to do? "

def Speech_Warp2_Repeat():
    if locale_de():
        return "Geradeaus oder nach rechts gehen? "
    else:
        return "Go straight ahead or right? "

def Speech_Warp3_1():
    if locale_de():
        return "Du springst auf Etage 3 und landest in einem einzelnen Raum. Du hörst ein Geräusch. "
    else:
        return "You warp to floor 3 and end up in a single room. You hear a noise. "

def Speech_Warp3_2():
    if locale_de():
        return "Das Loch, in das du gerade hinabgestiegen bist, wurde von der anderen Seite verschlossen. " \
               "Vor dir siehst du zwei leckere Sachen auf kleinen Holztischen, " \
               "einen Teller mit glasierten Donuts und auf dem anderen Tisch einen Biskuitkuchen. " \
               "Wofür entscheidest du dich?"
    else:
        return "The hole you just climbed down has been sealed from the other side. " \
               "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, " \
               "the other has a full Victoria sponge cake. Which do you choose? "

def Speech_Warp3_Repeat():
    if locale_de():
        return "Wofür entscheidest du dich? Nimmst du den Kuchen oder die Donuts? "
    else:
        return "Which do you choose? The cake or the doughnuts? "

def Speech_Warp_InvalidNumber():
    if locale_de():
        return "Diese Etage gibt es nicht, du kannst nur zu den Etagen eins, zwei und drei springen. "
    else:
        return "That floor does not exist, you can only warp to floors one, two and three. "

def Speech_Warp_InvalidString():
    if locale_de():
        return "Du kannst nicht zu dieser Etage springen. "
    else:
        return "You cannot warp to that floor. "

def Speech_Warp_Locked():
    if locale_de():
        return "Du hast die Sprungfunktion noch nicht entsperrt. "
    else:
        return "You have not unlocked warping yet. "

def Speech_Floor1_LeftInvalid():
    if locale_de():
        return "Du kannst hier nicht nach links gehen. "
    else:
        return "You can't go left here. "

def Speech_Floor1_RightInvalid():
    if locale_de():
        return "Du kannst hier nicht nach rechts gehen. "
    else:
        return "You can't go right here. "

def Speech_Floor1_Repeat_Barry():
    if locale_de():
        return "Zu Barry sprechen oder zurückgehen? "
    else:
        return "Talk to Barry or go back? "

def Speech_Floor1_Repeat_Larry():
    if locale_de():
        return "Zu Larry sprechen oder zurückgehen? "
    else:
        return "Talk to Larry or go back? "

def Speech_Floor1_Repeat_Entrance():
    if locale_de():
        return "Nach links oder nach rechts? "
    else:
        return "Go left or right? "

def Speech_Floor1_SpeakInvalid():
    if locale_de():
        return "Hier ist niemand, mit dem du sprechen könntest. "
    else:
        return "There is nobody to speak to here. "

def Speech_Floor1_NoEscape():
    if locale_de():
        return "Du bist in der Eingangshalle, es gibt kein Entkommen. "
    else:
        return "You are in the entrance hall, there is no escaping. "

def Speech_Floor1_BarrySaidNo():
    if locale_de():
        return "Larry sagt: Leider kann ich dich nicht gehen lassen. "
    else:
        return "Larry Says: Oh Too bad, sorry I can't let you go. "

def Speech_Floor1_BarrySaidYes_1():
    if locale_de():
        return "Larry wirkt überrascht, aber lässt dich die Leiter hinabsteigen. " \
               "Die Leiter endet in einem schwach. "
    else:
        return "Larry seems surprised but lets you climb down the ladder anyway. " \
               "The ladder stops in a dimly lit corridor. "

def Speech_Floor1_BarrySaidYes_2():
    if locale_de():
        return "Auf dem Boden ist etwas Rotes, Klebriges. " \
               "Du hörst das Geräusch von Metall auf Metall. "
    else:
        return "There is something red and sticky on the floor. " \
               "You can hear the clattering of metal. "

def Speech_Floor1_BarrySaidYes_3():
    if locale_de():
        return "Etwas bewegt sich hier unten. " \
               "Du kannst entweder vorwärts einen Korridor hinunter oder nach rechts in einen anderen Korridor gehen. " \
               "Was möchtest du tun?"
    else:
        return "Something is moving down here. " \
               "You can either go forward down one corridor or move right down another. " \
               "What would you like to do?"

def Speech_Floor2_Help():
    if locale_de():
        return "Auf dieser Etage kannst du die Figur bewegen. " \
               "Sage: „Vorwärts“, um in Blickrichtung der Figur zu gehen. " \
               "Sage: „Links“, um dich nach links zu wenden. " \
               "Sage: „Rechts“, um dich nach rechts zu wenden; sage „Zurück“, um wieder zurückzugehen. "
    else:
        return "On this floor you can move the character. " \
               "Say: forward, to move the direction the character is facing. " \
               "Say: left, to turn left. Say: right, to turn right, " \
               "Say: back, to turn around and go back to where you came from. "

def Speech_Floor2_InvalidDirection_F():
    if locale_de():
        return "Du kannst hier nicht vorwärts gehen. "
    else:
        return "You cannot move forward here. "

def Speech_Floor2_InvalidDirection_L():
    if locale_de():
        return "Du kannst hier nicht nach links gehen. "
    else:
        return "You cannot move left here. "

def Speech_Floor2_InvalidDirection_R():
    if locale_de():
        return "Du kannst hier nicht nach rechts gehen. "
    else:
        return "You cannot move right here. "

def Speech_Floor2_InvalidDirection_B():
    if locale_de():
        return "Es gibt kein Entkommen. "
    else:
        return "There is no escape. "

def Speech_Floor2_InvalidDirection_Continue():
    if locale_de():
        return "Die kannst hier nicht weiter vorwärts gehen. "
    else:
        return "You can't continue forward here. "

def Speech_Floor3_Start():
    if locale_de():
        return "Vor dir siehst du zwei leckere Sachen auf kleinen Holztischen, " \
               "einen Teller mit glasierten Donuts und auf dem anderen Tisch einen Biskuitkuchen. " \
               "Wofür entscheidest du dich? "
    else:
        return "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, " \
               "the other has a full Victoria sponge cake. Which do you choose? "

def Speech_Floor3_Help():
    if locale_de():
        return "Vor dir siehst du zwei leckere Sachen auf kleinen Holztischen, " \
               "einen Teller mit glasierten Donuts und auf dem anderen Tisch einen Biskuitkuchen. " \
               "Um den Kuchen zu wählen, sage: „Kuchen“. Um die Donuts zu wählen, sage: „Donuts“. " \
               "Wählst du den Kuchen oder die Donuts? "
    else:
        return "Ahead of you are two treats on small wooden tables, one has a plate of sugared doughnuts, " \
               "the other has a full Victoria sponge cake. To choose the cake, Say: Cake. " \
               "To choose the doughnuts, Say: Doughnuts. Do you choose the cake or the doughnuts? "

def Speech_Floor3_Repeat():
    if locale_de():
        return "Wofür entscheidest du dich? Nimmst du den Kuchen oder die Donuts? "
    else:
        return "Which do you choose? The cake or the doughnuts? "

def Speech_Floor3_Cake():
    if locale_de():
        return "Du nimmst ein Stück von dem Biskuitkuchen. Dies ist der beste Kuchen, den du je gegessen hast. " \
               "Plötzlich beginnst du, heftig zu husten. Du wurdest vergiftet. " \
               "Du drehst dich um und siehst eine Geisterritterrüstung. Diese sagt: „Danke, ich bin frei. " \
               "Der Geist verlässt die Rüstung und verschwindet im Nichts. Du fällst in Ohnmacht. " \
               "Als du erwachst, hast du keinen Körper, du bist ein Geist in dieser Ritterrüstung, " \
               "dazu verurteilt, immer in diesen Räumen hin und her zu gehen. Ende. " \
               "In künftigen Spielen kannst du „Zu Etage X springen“ sagen, " \
               "um einen beliebigen Teil erneut zu spielen. Vielen Dank für das Spiel! "
    else:
        return "You take a slice of Victoria sponge cake. It's the most delicious cake you've ever eaten. " \
               "Suddenly you start coughing violently. You have been poisoned. " \
               "You turn around to find a haunted suit of armour. He says: I'm free thank you. " \
               "The spirit possessing the armour, leaves the suit and fades away into nothingness. " \
               "You black out. You awake to find you have no body, " \
               "you are a spirit possessing the same suit of armour, " \
               "doomed to walk these halls forever. The End. On future replays you can say, warp to floor X, " \
               "to replay any part you like. Thank you for playing! "

def Speech_Floor3_Doughnuts():
    if locale_de():
        return "Die beginnst, die Donuts zu essen. Sie haben einen Geschmack, den du noch niemals erlebt hast. " \
               "Dies sind die besten Donuts, die du jemals gegessen hast; plötzlich fühlst du einen Schmerz im Bauch. " \
               "Du wurdest vergiftet. Du drehst dich um und siehst ein bekanntes Gesicht. Es ist Larry. " \
               "Er sagt: Vielen Dank, ich kann jetzt weitergehen. Er verschwindet im Nichts. Du fällst in Ohnmacht. " \
               "Du wachst am oberen Ende der ersten Leiter auf, " \
               "siehst an dir herunter – du bist durchsichtig und schwebst. " \
               "Du trägst ein Namensschild mit der Aufschrift „Larry“. Ende. " \
               "In künftigen Spielen kannst du „Zu Etage X springen“ sagen, " \
               "um einen beliebigen Teil erneut zu spielen. Vielen Dank für das Spiel! "
    else:
        return "You start eating the doughnuts. The insides ooze with a flavour you've never tasted before. " \
               "They are the most delicious doughnuts you've ever eaten, you get a sudden pain in the stomach. " \
               "You have been poisoned. You look back to find a familiar face. It's Larry. " \
               "He says: Thank you, I can now move on. He fades away into nothingness. You black out. " \
               "You awake at the top of the first ladder, you look down at yourself, " \
               "you're transparent and floating, You are wearing a nametag, it says Larry. The End. " \
               "On future replays you can say, warp to floor X, to replay any part you like. Thank you for playing! "

def Speech_Floor3_Both():
    if locale_de():
        return "Du isst einen Donut. Du fühlst einen plötzlichen Schmerz im Bauch. " \
               "Du nimmst schnell einen Bissen von dem Kuchen. Der Schmerz verschwindet so schnell, " \
               "wie er gekommen ist. Du drehst dich um und siehst ein bekanntes Gesicht. Es ist Barry. " \
               "Er lacht und sagt: „Dummkopf, sie sind vergiftet und du bist jetzt mein Gefangener.“ " \
               "Du und Barry warten einen unangenehmen Moment lang. „Ich verstehe das nicht“, " \
               "ruft Barry, „Das Gift in beiden Speisen muss sich doch gegenseitig aufheben.“ " \
               "Ihr starrt euch eine Weile lang an. Barry bringt dich nicht dazu, das Gift zu nehmen, " \
               "und du kannst einen Geist nicht angreifen. Du verlässt das geheimnisvolle Haus. " \
               "Du hast das Geheimnis gelöst und überlebt – Barry bleibt verärgert zurück. Ende. " \
               "In künftigen Spielen kannst du „Zu Etage X springen“ sagen, um einen beliebigen Teil " \
               "erneut zu spielen. Vielen Dank für das Spiel! "
    else:
        return "You eat a doughnut. You get a sudden pain in the stomach. You quickly take a bite of cake. " \
               "The pain stopped as suddenly as it started. You look back to find a familiar face. It's Barry. " \
               "He laughs and says, fool, they were poisoned and now you'll be my prisoner. B" \
               "oth you and Barry wait for an awkward amount of time. I don't understand, exclaimed Barry, " \
               "the poison in both foods must cancel each other out. You and Barry stare at each other for a while. " \
               "Barry can't trick you into taking poison, and you can't attack a ghost. " \
               "You leave the mysterious house. You solved the mystery and survived, leaving an irked Barry behind. " \
               "The End. On future replays you can say, warp to floor X, to replay any part you like. " \
               "Thank you for playing! "

def Speech_Floor3_Invalid():
    if locale_de():
        return "Ich habe das nicht verstanden, möchtest du den Kuchen oder die Donuts? "
    else:
        return "I'm sorry I didn't understand that, do you want the cake or the doughnuts? "

def Speech_Floor3_Invalid_Repeat():
    if locale_de():
        return "Wofür entscheidest du dich? Nimmst du den Kuchen oder die Donuts? "
    else:
        return "Which do you choose? The cake or the doughnuts? "

# --------------- Text Card Titles

def Title_Start():
    if locale_de():
        return "Du kommst zu einem geheimnisvollen Haus"
    else:
        return "You arrive at a mysterious house"

def Title_Load_Floor2():
    if locale_de():
        return "Gespeichertes Spiel geladen – Etage 2"
    else:
        return "Game Save Loaded - Floor 2"

def Title_Load_Floor3():
    if locale_de():
        return "Gespeichertes Spiel geladen – Etage 3"
    else:
        return "Game Save Loaded - Floor 3"

def Title_End():
    if locale_de():
        return "Vielen Dank für dein Spiel!"
    else:
        return "Thanks for playing!"

def Title_Floor1_X0():
    if locale_de():
        return "Barry, der Geist"
    else:
        return "Barry the Ghost"

def Title_Floor1_Entrance():
    if locale_de():
        return "Linke oder rechte Tür?"
    else:
        return "Left or right Door?"

def Title_Floor1_Larry():
    if locale_de():
        return "Larry, der Geist"
    else:
        return "Larry the Ghost"

def Title_Floor1_Barry_Reply():
    if locale_de():
        return "Barry sagt „Nein“"
    else:
        return "Barry says No"

def Title_Floor1_Barry_InitialSpeech():
    if locale_de():
        return "Barry scheint wütend zu sein"
    else:
        return "Barry seems angry"

def Title_Floor2_Caught():
    if locale_de():
        return "Du bist gefangen!"
    else:
        return "You got caught!"

def Title_Floor2_Prompt():
    if locale_de():
        return "Wohin jetzt?"
    else:
        return "Where to move?"

def Title_Warp2():
    if locale_de():
        return "Sprung zu Etage 2"
    else:
        return "Warp to floor 2"

def Title_Warp3():
    if locale_de():
        return "Sprung zu Etage 3"
    else:
        return "Warp to floor 3"

def Title_Invalid():
    if locale_de():
        return "Ungültige Aktion"
    else:
        return "Invalid Action"

def Title_Floor2_RepeatHelp():
    if locale_de():
        return "Wie möchtest du dich bewegen?"
    else:
        return "How do you want to move?"

def Title_Floor3_Choice():
    if locale_de():
        return "Wofür entscheidest du dich?"
    else:
        return "What do you choose?"

def Title_Floor3_Cake():
    if locale_de():
        return "Du hast den Kuchen gegessen"
    else:
        return "You ate the cake"

def Title_Floor3_Doughnut():
    if locale_de():
        return "Du hast die Donuts gegessen"
    else:
        return "You ate the doughnuts"

def Title_Floor3_Both():
    if locale_de():
        return "Du hast die Donuts und den Kuchen gegessen"
    else:
        return "You ate both the doughnuts and the cake"

# --------------- Responses

def get_start_response():
    return get_audio_response(
        get_starting_floor1_attributes(),
        Title_Start(),
        Speech_Start_1() ,
        door_sound(),
        Speech_Start_2(),
        Speech_Start_repeat()
    )

def initial_load_response(userID):
    floor_number = LoadFloorNumber(userID)
    if (floor_number == 1):
        return get_start_response()
    elif (floor_number == 2):
        return get_doubleaudio_response(
            get_starting_floor2_attributes(),
            Title_Load_Floor2(),
            Speech_Load_Floor2_1(),
            jam_sound(),
            Speech_Load_Floor2_2(),
            armour_sound(),
            Speech_Load_Floor2_3(),
            Speech_Load_Floor2_repeat()
        )
    elif (floor_number == 3):
        return get_audio_response(
            get_starting_floor3_attributes(),
            Title_Load_Floor3(),
            Speech_Load_Floor3_1(),
            hatch_sound(),
            Speech_Load_Floor3_2(),
            Speech_Load_Floor3_repeat()
        )
    else:
        return get_start_response()

def get_end_response():
    return get_audio_response(
        {},
        Title_End(),
        Speech_End(),
        jingle_sound(),
        "",
        None,
        True
    )

def get_misunderstood_response(session_attributes):
    return get_response(
        session_attributes,
        Title_Invalid(),
        Speech_misunderstood(),
        Speech_misunderstood()
    )

def get_error_response(error_code):
    return get_response(
        {},
        Title_Invalid(),
        Speech_error(error_code),
        None,
        True
    )

# --------------- Floor 1

def get_floor1_situation(x, visited_larry, visited_barry, session_attributes, play_door, warp_text = "", help_request = False):
    if x == 0:

        help_text = ""
        if help_request:
            help_text = Speech_Floor1_X0_Help()

        if visited_barry:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    Title_Floor1_X0(),
                    "",
                    door_sound(),
                    warp_text + Speech_Floor1_X0_Revisit_1() + help_text +
                    Speech_Floor1_X0_Revisit_2(),
                    Speech_Floor1_X0_Visit_Rep()
                )
            else:
                return get_response(
                    session_attributes,
                    Title_Floor1_X0(),
                    warp_text + Speech_Floor1_X0_Revisit_1() + help_text +
                    Speech_Floor1_X0_Revisit_2(),
                    Speech_Floor1_X0_Visit_Rep()
                )
        else:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    Title_Floor1_X0(),
                    "",
                    door_sound(),
                    warp_text + Speech_Floor1_X0_Visit_1() +
                    help_text  + Speech_Floor1_X0_Visit_2(),
                    Speech_Floor1_X0_Visit_Rep()
                )
            else:
                return get_response(
                    session_attributes,
                    Title_Floor1_X0(),
                    warp_text + Speech_Floor1_X0_Visit_1() +
                    help_text + Speech_Floor1_X0_Visit_2(),
                    Speech_Floor1_X0_Visit_Rep()
                )
    elif x == 1:

        help_text = ""
        if help_request:
            help_text = Speech_Floor1_X1_Help()

        if play_door:
            print(warp_text)
            return get_audio_response(
                session_attributes,
                Title_Floor1_Entrance(),
                warp_text,
                 door_sound(),
                Speech_Floor1_X1_Revisit_1() + help_text +
                Speech_Floor1_X1_Revisit_2(),
                Speech_Floor1_X1_Visit_Rep()
            )
        elif not visited_larry and not visited_barry:
            return get_response(
                session_attributes,
                Title_Floor1_Entrance(),
                warp_text + Speech_Floor1_X1_Visit_1() + help_text +
                Speech_Floor1_X1_Visit_2(),
                Speech_Floor1_X1_Visit_Rep()
            )
        else:
            return get_response(
                session_attributes,
                Title_Floor1_Entrance(),
                warp_text + Speech_Floor1_X1_Revisit_1() + help_text +
                Speech_Floor1_X1_Revisit_2(),
                Speech_Floor1_X1_Visit_Rep()
            )
    elif x == 2:

        help_text = ""
        if help_request:
            help_text = Speech_Floor1_X2_Help()

        if visited_larry:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    Title_Floor1_Larry(),
                    warp_text,
                    door_sound(),
                    Speech_Floor1_X2_Revisit_1() + help_text +
                    Speech_Floor1_X2_Revisit_2(),
                    Speech_Floor1_X2_Visit_Rep()
                )
            else:
                return get_response(
                    session_attributes,
                    Title_Floor1_Larry(),
                    warp_text + Speech_Floor1_X2_Revisit_1() + help_text +
                    Speech_Floor1_X2_Revisit_2(),
                    Speech_Floor1_X2_Visit_Rep()
                )
        else:
            if play_door:
                return get_audio_response(
                    session_attributes,
                    Title_Floor1_Larry(),
                    warp_text,
                    door_sound(),
                    Speech_Floor1_X2_Visit_1() +
                    help_text +
                    Speech_Floor1_X2_Visit_2(),
                    Speech_Floor1_X2_Visit_Rep()
                )
            else:
                return get_response(
                    session_attributes,
                    Title_Floor1_Larry(),
                    warp_text +
                    Speech_Floor1_X2_Visit_1() +
                    help_text +
                    Speech_Floor1_X2_Visit_2(),
                    Speech_Floor1_X2_Visit_Rep()
                )
    else:
        return get_error_response("One")

def get_barry_speech(spoken_to_barry, spoken_to_larry, visited_larry):
    if spoken_to_barry:
        return get_response(
            construct_floor1_attributes(0, True, True, True, True, False),
            Title_Floor1_Barry_Reply(),
            Speech_Floor1_BarryAsk_Revisit(),
            Speech_Floor1_BarryAsk_Revisit_Repeat()
        )
    elif spoken_to_larry:
        return get_response(
            construct_floor1_attributes(0, True, True, True, True, False),
            Title_Floor1_Barry_Reply(),
            Speech_Floor1_BarryAsk(),
            Speech_Floor1_BarryAsk_Repeat()
        )
    else:
        return get_response(
            construct_floor1_attributes(0, True, visited_larry, False, False, False),
            Title_Floor1_Barry_InitialSpeech(),
            Speech_Floor1_BarryInitial(),
            Speech_Floor1_BarryInitial_Repeat()
        )

def get_larry_speech(spoken_to_barry, spoken_to_larry, visited_barry):
    if spoken_to_larry:
        if spoken_to_barry:
            return get_response(
                construct_floor1_attributes(2, True, True, True, True, True),
                Title_Floor1_Larry(),
                Speech_Floor1_Larry_PostBarry(),
                Speech_Floor1_Larry_PostBarry()
            )
        else:
            return get_response(
                construct_floor1_attributes(2, visited_barry, True, False, True, False),
                Title_Floor1_Larry(),
                Speech_Floor1_Larry_Revisit(),
                Speech_Floor1_Larry_Repeat()
            )
    else:
        return get_response(
            construct_floor1_attributes(2, visited_barry, True, False, True, False),
            Title_Floor1_Larry(),
            Speech_Floor1_Larry(),
            Speech_Floor1_Larry_Repeat()
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
        return [Speech_Floor2_Start(),
                Speech_Floor2_Start_Repeat()]

    directions = get_floor2_directions(osstate, x, y)
    forward = directions[0]
    backward = directions[1]
    left = directions[2]
    right = directions[3]

    if forward:
        if backward:
            if left:
                if right:
                    return [Speech_Floor2_FLRB(), Speech_Floor2_FLRB_Repeat()]
                else:
                    return [Speech_Floor2_FLB(), Speech_Floor2_FLB_Repeat()]
            elif right:
                return [Speech_Floor2_FRB(), Speech_Floor2_FRB_Repeat()]
            else:
                return ["You have reached a set or crates, would you like to go past or go back the way you came?",
                        "would you like to keep going or go back?"]
        elif left:
            if right:
                return [Speech_Floor2_FLR(), Speech_Floor2_FLR_Repeat()]
            else:
                return [Speech_Floor2_FL(), Speech_Floor2_FL_Repeat()]
        elif right:
            return  [Speech_Floor2_FR(), Speech_Floor2_FR_Repeat()]
        else:
            return ["You have reached a set or crates, would you like to keep going?",
                    "Would you like to keep going forward?"]
    elif backward:
        if left:
            if right:
                return [Speech_Floor2_LRB(), Speech_Floor2_LRB_Repeat()]
            else:
                return [Speech_Floor2_LB(), Speech_Floor2_LB_Repeat()]
        elif right:
            return [Speech_Floor2_RB(), Speech_Floor2_RB_Repeat()]
        else:
            return ["You have reached a dead end, would you like to go back the way you came?",
                    "A dead end, would you like to go back the way you came?"]
    elif left:
        if right:
            return [Speech_Floor2_LR(), Speech_Floor2_LR_Repeat()]
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
            Title_Floor2_Caught(),
            flavour_text + Speech_Floor2_Armour_1(),
            armour_sound(),
            Speech_Floor2_Armour_2(),
            Speech_Floor2_Armour_Repeat()
        )

    # End Detection
    elif is_at_floor2_end(x, y):
        SaveFloorNumber(userId, 3)
        return  get_audio_response(
            get_starting_floor3_attributes(),
            Title_Floor3_Choice(),
            flavour_text + Speech_Floor2_End_1(),
            hatch_sound(),
            Speech_Floor2_End_2(),
            Speech_Floor2_End_Repeat()
        )

    # Normal Update
    else:
        movement_options = get_floor2_movement_options_state(osstate, x, y)
        return get_response(
            construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
            Title_Floor2_Prompt(),
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
        return get_move_response(osstate, x, y, Speech_Floor2_Action_F(), mob_x, mob_y, userId)


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
        return get_move_response(osstate, x, y, Speech_Floor2_Action_B(), mob_x, mob_y, userId)


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
            flavour_text = Speech_Floor2_Action_LF()
        else:
            flavour_text = Speech_Floor2_Action_L()
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
            flavour_text = Speech_Floor2_Action_RF()
        else:
            flavour_text = Speech_Floor2_Action_R()
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
                    Title_Warp2(),
                    Speech_Warp2_1(),
                    jam_sound(),
                    Speech_Warp2_2(),
                    armour_sound(),
                    Speech_Warp2_3(),
                    Speech_Warp2_Repeat()
                )
            elif (floor_number == '3'):
                response = get_audio_response(
                    get_starting_floor3_attributes(),
                    Title_Floor3_Choice(),
                    Speech_Warp3_1(),
                    hatch_sound(),
                    Speech_Warp3_2(),
                    Speech_Warp3_Repeat()
                )
            elif session.get('attributes', {}) and "Floor" in session.get('attributes', {}):
                isError = True
                response = Speech_Warp_InvalidNumber()
            else:
                response = get_start_response()
        elif session.get('attributes', {}) and "Floor" in session.get('attributes', {}):
            isError = True
            response = Speech_Warp_InvalidString()
    else:
        if session.get('attributes', {}) and "Floor" in session.get('attributes', {}):
            isError = True
            response = Speech_Warp_Locked()
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
                Title_Invalid(),
                Speech_Floor1_LeftInvalid(),
                Speech_Floor1_Repeat_Barry()
            )
        else:
            return  get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                Title_Invalid(),
                Speech_Floor1_LeftInvalid(),
                Speech_Floor1_Repeat_Larry()
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
                Title_Invalid(),
                Speech_Floor1_RightInvalid(),
                Speech_Floor1_Repeat_Barry()
            )
        else:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                Title_Invalid(),
                Speech_Floor1_RightInvalid(),
                Speech_Floor1_Repeat_Larry()
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
                Title_Invalid(),
                Speech_Floor1_NoEscape(),
                Speech_Floor1_Repeat_Entrance()
            )
    elif intent_name == "TalkIntent" or \
                    intent_name == "TalkToLarryIntent" or \
                    intent_name == "TalkToBarryIntent":
        if x == 0:
            return get_barry_speech(spoken_to_barry, spoken_to_larry, visited_larry)
        elif x == 2:
            return  get_larry_speech(spoken_to_barry, spoken_to_larry, visited_barry)
        else:
            return  get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, spoken_to_barry,
                                            spoken_to_larry, asking_larry),
                Title_Invalid(),
                Speech_Floor1_SpeakInvalid(),
                Speech_Floor1_Repeat_Entrance()
            )
    elif intent_name == "AMAZON.NoIntent" or intent_name == "BarrySaidNoIntent":
        if asking_larry:
            return get_response(
                construct_floor1_attributes(x, visited_barry, visited_larry, False,
                                            spoken_to_larry, False),
                Title_Floor1_Larry(),
                Speech_Floor1_BarrySaidNo()
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
                Title_Floor2_Prompt(),
                Speech_Floor1_BarrySaidYes_1(),
                jam_sound(),
                Speech_Floor1_BarrySaidYes_2(),
                armour_sound(),
                Speech_Floor1_BarrySaidYes_3()
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
            Title_Floor2_Prompt(),
            warp_text + movement_options[0],
            movement_options[1]
        )
    elif intent_name == "AMAZON.HelpIntent":
        movement_options = get_floor2_movement_options_state(osstate, x, y)
        return get_response(
            construct_floor2_attributes(x, y, osstate, mob_x, mob_y),
            Title_Floor2_Prompt(),
            Speech_Floor2_Help() + movement_options[0],
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
                Title_Invalid(),
                Speech_Floor2_InvalidDirection_F(),
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
                Title_Invalid(),
                Speech_Floor2_InvalidDirection_B(),
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
                Title_Invalid(),
                Speech_Floor2_InvalidDirection_L(),
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
                Title_Invalid(),
                Speech_Floor2_InvalidDirection_R(),
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
                Title_Invalid(),
                Speech_Floor2_InvalidDirection_Continue(),
                movement_options[1]
            )
    return get_misunderstood_response(
        construct_floor2_attributes(x, y, osstate, mob_x, mob_y))


def on_intent_floor3(intent_name, session, userId, warp_text):
    # No attributes just intent checks
    if intent_name == "AMAZON.RepeatIntent" or intent_name == "PlayIntent" or intent_name == "WarpIntent":
        return get_response(
            get_starting_floor3_attributes(),
            Title_Floor3_Choice(),
            warp_text +
            Speech_Floor3_Start(),
            Speech_Floor3_Repeat()
        )
    elif intent_name == "AMAZON.HelpIntent":
        return get_response(
            get_starting_floor3_attributes(),
            Title_Floor3_Choice(),
            Speech_Floor3_Help(),
            Speech_Floor3_Repeat()
        )
    # Cake
    elif intent_name == "CakeIntent":
        SaveAll(userId, True, 1)
        return get_audio_response(
            {},
            Title_Floor3_Cake(),
            Speech_Floor3_Cake(),
            jingle_sound(),
            "",
            None,
            True # End Game Here
        )
    elif intent_name == "DoughnutIntent":
        SaveAll(userId, True, 1)
        return get_audio_response(
            {},
            Title_Floor3_Doughnut(),
            Speech_Floor3_Doughnuts(),
            jingle_sound(),
            "",
            None,
            True  # End Game Here
        )
    elif intent_name == "BothTreatsIntent":
        SaveAll(userId, True, 1)
        return get_audio_response(
            {},
            Title_Floor3_Both(),
            Speech_Floor3_Both(),
            jingle_sound(),
            "",
            None,
            True  # End Game Here
        )
    else:
        return get_response(
            get_starting_floor3_attributes(),
            Title_Floor3_Choice(),
            Speech_Floor3_Invalid(),
            Speech_Floor3_Invalid_Repeat()
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

    global locale
    locale = event['request']['locale']
    print("locale is " + locale)

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
