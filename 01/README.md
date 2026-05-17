# 1주차 과제 : CLI 프로그램 만들기
## 프로그램 목적
이번주 교육일정을 마치며 매일 해야 할 일이 쌓여져가는데 일정 정리하는게 다소 복잡하여 도움을 주는 툴을 만들고자 한다.

## 프로그램 설명
1) 디데이 날짜 순서대로 내가 해야 할 일을 보여줌
2) 매일 해야 할 일을 해야 할 순서에 맞게 보여줌

## 프로그램 기능
두가지 기능 (Show, Add)
1. Show  1) D-day Todo List나 Everyday Todo List 두 가지 중 하나를 보여준다.
         2) 두개의 Todo List를 한꺼번에 보여준다.
2. Add   1) D-day 날짜가 존재하는 일을 디데이 날짜와 함께 입력한다.
         2) 매일 해야 할 일을 해야하는 순서와 함께 입력한다.

## How to use
```
# Todo List 조회
python3 todo.py show --todo <원하는 디데이 목록(choices: dday, everyday, all>

# Todo List Add (D-day 있는 할 일)
python3 todo.py adddday --dday <디데이 날짜(YY-MM-DD)>

# Todo List Add (매일 해야 할 일)
python3 todo.py addeveryday --ordernum <해야 할 순서>
```

## 실행 예시


## 회고
기능 구현을 위해 웹검색은 불가피하였기 때문에 AI는 되도록 사용하지 않으려 했는데 구글링하면 상단에 자동으로 AI 답변이 떠서 난감하다.

