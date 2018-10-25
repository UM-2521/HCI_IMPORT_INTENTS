# 원본 출처: http://ndb796.tistory.com/127?category=1013435
import openpyxl


class Intent:
    """ 한 건의 대화(질문과 답변 1개씩)에 대한 정보를 담는 객체입니다.
        질문(Question), 응답(Answer) 두 매개변수를 받아 한 건의 질문-대답 인텐트를 생성합니다.
        이 고유 이름에 따라 Dialogflow에 Intent가 따로 분류되어 들어갑니다.
    """
    current_index = 1

    def __init__(self, question, answer):
        self.name = "Kakaotalk" + str(Intent.current_index)
        Intent.current_index += 1

        self.question = question
        self.answer = answer

    def __str__(self):
        return "질문: " + self.question + "\n답변: " + self.answer + "\n"


if __name__ == "__main__":
    """ 카카오톡 대화 내용을 저장해둔 엑셀 파일을 열어서 데이터를 가져와
        Dialogflow에 넣을 수 있는 형태로 정보를 가공합니다.        
    """
    wb = openpyxl.load_workbook('test.xlsx')
    ws = wb.active

    # Intent 객체를 만들기 전 질문/대답들을 모두 담아두는 리스트를 만듭니다.
    chat_list = []
    # 아바타를 만들 대상의 카카오톡 이름을 넣어줍니다.
    MY_NAME = "엄민식"

    # 엑셀 내부 데이터를 쭉 돌아가며 처리를 합니다.
    for r in ws.rows:

        # 빈줄은 넘어갑니다.
        if r is None:
            continue

        # 데이터를 받아 ] 단위로 텍스트를 쪼개 저장합니다.
        data = r[0].value.split(']')

        # 채팅 메세지 이외의 텍스트는 ']' 가 없기에 쪼개지 않고 크기가 1인 리스트로 반환됩니다.
        # 채팅 메세지 이외의 텍스트는 처리를 하지 않고 버리고 넘어갑니다.
        if len(data) == 1:
            continue

        # 메세지 보낸 사람을 저장합니다.
        message_sender = data[0][1:].strip()
        # 대화 텍스트를 저장합니다.
        user_message = data[2].strip()

        if not chat_list:
            # chat_list 에 아직 담긴 게 없으면 그냥 넣어줍니다.
            chat_list.append([message_sender, user_message])
        else:
            # 한 사람이 계속해서 말하면 뒤에 붙여주고 다른 사람 말이면 새로 메세지를 넣어줍니다.
            if chat_list[-1][0] == message_sender:
                chat_list[-1][1] += " " + user_message
            else:
                chat_list.append([message_sender, user_message])

    wb.close()

    ''' 자신의 아바타를 만드는 것이므로 답변이 나의 메세지, 질문이 상대방이어야 합니다.
        자신이 먼저 질문한 형태라면 앞의 1개를 빼주어 상대가 마치 먼저 질문한 것처럼 수정해줍니다.
    '''
    if chat_list[0][0] == MY_NAME:
        chat_list.pop(0)

    ''' 질문과 대답의 개수가 동일한지 검사합니다. 같아야 전부 Intent로 생성할 수 있습니다.
        첫과 끝 사람이 똑같아 질문 개수가 1개 더 많아 다르다면 뒤의 1개를 빼줍니다.
    '''
    if chat_list[0][0] == chat_list[-1][0]:
        chat_list.pop()

    # 개수가 짝수개이므로 2로 나눠서 Intent 객체를 생성해줍니다.
    Intents = [Intent(chat_list[i][1], chat_list[i + 1][1])
               for i in range(0, len(chat_list), 2)]

    # 모든 대화 내용을 콘솔에 출력하여 잘 받아왔는지 확인합니다.
    for c in Intents:
        print(str(c))

    print('총 ', len(Intents), '개의 질문-대답이 존재합니다.')

    """ 이후 코드는 원 출처(코드 최상단 주석 참고)의 코드와 동일합니다.
        intent 객체들로 저장된 데이터를 데이터 형식에 맞추어 텍스트를 만들고
        .json 확장자의 파일로 저장합니다.
    """

    i = 1
    prev = Intents[0].name
    f = open(prev + '.json', 'w', encoding='UTF-8')

    f.write('{ "id": "10d3155d-4468-4118-8f5d-15009af446d0", "name": "'
            + prev
            + '", "auto": true, "contexts": [], "responses": [ { "resetContexts": false, "affectedContexts": [], "parameters": [], "messages": [ { "type": 0, "lang": "ko", "speech": "'
            + Intents[0].answer
            + '" } ], "defaultResponsePlatforms": {}, "speech": [] } ], "priority": 500000, "webhookUsed": false, "webhookForSlotFilling": false, "fallbackIntent": false, "events": [] }')
    f.close()

    f = open(prev + '_usersays_ko.json', 'w', encoding='UTF-8')
    f.write("[")
    f.write('{ "id": "3330d5a3-f38e-48fd-a3e6-000000000001", "data": [ { "text": "'
            + Intents[0].question
            + '", "userDefined": false } ], "isTemplate": false, "count": 0 },')

    while True:
        if i >= len(Intents):
            f.write("]")
            f.close()
            break

        c = Intents[i]

        if prev == c.name:
            f.write('{ "id": "3330d5a3-f38e-48fd-a3e6-000000000001", "data": [ { "text": "' + c.question + '", "userDefined": false } ], "isTemplate": false, "count": 0 },')
        else:
            f.write("]")
            f.close()

            prev = c.name
            f = open(prev + '.json', 'w', encoding='UTF-8')
            f.write(
                '{ "id": "10d3155d-4468-4118-8f5d-15009af446d0", "name": "'
                + prev
                + '", "auto": true, "contexts": [], "responses": [ { "resetContexts": false, "affectedContexts": [], "parameters": [], "messages": [ { "type": 0, "lang": "ko", "speech": "' + c.answer + '" } ], "defaultResponsePlatforms": {}, "speech": [] } ], "priority": 500000, "webhookUsed": false, "webhookForSlotFilling": false, "fallbackIntent": false, "events": [] }')
            f.close()

            f = open(prev + '_usersays_ko.json', 'w', encoding='UTF-8')
            f.write("[")
            f.write('{ "id": "3330d5a3-f38e-48fd-a3e6-000000000001", "data": [ { "text": "' + c.question + '", "userDefined": false } ], "isTemplate": false, "count": 0 },')

        i = i + 1
