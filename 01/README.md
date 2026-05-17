# 1주차 과제 : CLI 프로그램 만들기
## 프로그램 목적
이번주 교육일정을 마치며 매일 해야 할 일이 쌓여져가는데 일정 정리하는게 다소 복잡하여 도움을 주는 툴을 만들고자 한다.

## 프로그램 설명
1) 디데이 날짜 순서대로 내가 해야 할 일을 보여줌
2) 매일 해야 할 일을 해야 할 순서에 맞게 보여줌

## 프로그램 기능
세 가지 기능 (Show, Add, Delete)
1. Show  1) D-day Todo List나 Everyday Todo List 두 가지 중 하나를 보여준다.
         2) 두개의 Todo List를 한꺼번에 보여준다.
2. Add   1) D-day 날짜가 존재하는 일을 디데이 날짜와 함께 입력한다.
         2) 매일 해야 할 일을 해야하는 순서와 함께 입력한다.
3. Delete : 일정을 삭제 한다.

## How to use
```
# Todo List 조회
python3 todo.py show --todo <원하는 디데이 목록(choices: dday, everyday, all>

# Todo List Add (D-day 있는 할 일 추가)
python3 todo.py adddday --dday <디데이 날짜(YY-MM-DD)>

# Todo List Add (매일 해야 할 일 추가)
python3 todo.py addeveryday --ordernum <해야 할 순서>

# Todo List Delete (D-day 있는 할 일 삭제)
python3 todo.py deldday --dday "<디데이 날짜(YY-MM-DD)>"

# Todo List Delete (매일 해야 할 일 삭제)
python3 todo.py deleveryday --ordernum <삭제할 일정의 순서>
```

## 실행 예시
```
# 먼저 show를 하기 위해서는 adddday나 addeveryday 가 진행되어야 한다.

# 아무것도 추가 안 한 상태일시 show 예시
% python3 todo.py show --todo dday
You need to add <D-day Todo List> first
% python3 todo.py show --todo everyday
You need to add <Everyday Todo List> first

# D-day 날짜가 존재하는 일정 추가
% python3 todo.py adddday --dday 26-05-17
New D-day List
Enter your content: Weekly Challenge Week 1
# 추가 후 확인
% python3 todo.py show --todo dday       
----------- D-day Todo List ------------------------------------------------------------------
|26-05-17    | Weekly Challenge Week 1                                                         |
----------------------------------------------------------------------------------------------

# 이미 존재하는 D-day 날짜 입력시 날짜 뒤에 숫자를 붙여줌
% python3 todo.py adddday --dday 26-05-17
Current D-day Todo List
----------- D-day Todo List ------------------------------------------------------------------
|26-05-17    | Weekly Challenge Week 1                                                         |
----------------------------------------------------------------------------------------------
Same d-day date!!
'26-05-17' changed to '26-05-17(2)'
Enter your content: Weekly Challenge Week 1 Same Date
% python3 todo.py show --todo dday       
----------- D-day Todo List ------------------------------------------------------------------
|26-05-17    | Weekly Challenge Week 1                                                         |
|26-05-17(2) | Weekly Challenge Week 1 Same Date                                               |
----------------------------------------------------------------------------------------------


# 매일 해야 할 일정 추가
% python3 todo.py addeveryday --ordernum 1
Enter your content: First thing I should do
% python3 todo.py show --todo everyday    
----------- Everyday Todo List ---------------------------------------------------------------
| 1  | First thing I should do                                                                 |
----------------------------------------------------------------------------------------------

# 매일 해야 할 일정에서 순서를 바꾸고 싶으면 넣고 싶은 위치를 적어주면 됨.
% python3 todo.py addeveryday --ordernum 1
Current Everyday Todo List
 ----------- Everyday Todo List --------------------------------------------------------------
| 1  | First thing I should do                                                                 |
 ---------------------------------------------------------------------------------------------
Order will be changed
Enter your content: Real First thing
% python3 todo.py show --todo everyday    
 ----------- Everyday Todo List --------------------------------------------------------------
| 1  | Real First thing                                                                        |
| 2  | First thing I should do                                                                 |
 ---------------------------------------------------------------------------------------------

# D-day 일정 삭제
% python3 todo.py deldday --dday 26-05-17
26-05-17 Deleted
% python3 todo.py show --todo dday       
 ----------- D-day Todo List -----------------------------------------------------------------
|26-05-17(2) | Weekly Challenge Week 1 Same Date                                               |
 ---------------------------------------------------------------------------------------------

# 매일 일정 삭제
% python3 todo.py deleveryday --ordernum 1
1 Deleted
% python3 todo.py show --todo everyday    
 ----------- Everyday Todo List --------------------------------------------------------------
| 1  | First thing I should do                                                                 |
 ---------------------------------------------------------------------------------------------

# 일정 전체 조회
% python3 todo.py show --todo all         
 ----------- D-day Todo List -----------------------------------------------------------------
|26-05-17(2) | Weekly Challenge Week 1 Same Date                                               |
 ---------------------------------------------------------------------------------------------
 ----------- Everyday Todo List --------------------------------------------------------------
| 1  | First thing I should do                                                                 |
 ---------------------------------------------------------------------------------------------
```
## 주의사항
삭제 실행시 --dday 인자 넘겨줄 시 따옴표 필수
e.g.) python3 todo.py deldday --dday "26-05-17(2)"

## 필요한 추가 기능
D-day Todo List 에서 일정 삭제시 동일한 날짜의 D-day를 가진 일정이 있을 경우 그 일정의 D-day 형식을 바꿔줘야함.
e.g.) 26-05-17과 26-05-17(2) 가 존재할 경우, 26-05-17를 삭제 시, 26-05-17(2)를 26-05-17로 바꿔줘야함

## 회고
기능 구현을 위해 웹검색은 불가피하였기 때문에 AI는 되도록 사용하지 않으려 했는데 구글링하면 상단에 자동으로 AI 답변이 떠서 난감하다.
파이썬의 다양한 기능을 검색 도움 없이도 코딩할 수 있도록 능력 향상이 필요하다. 
