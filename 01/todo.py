import pickle
import os
import argparse

everyday_path = 'everydaylist.pickle'
dday_path = 'ddaylist.pickle'

def show_list(todo):
    if todo == 'dday':
        show_dday()
    elif todo == 'everyday':
        show_everyday()
    elif todo == 'all':
        show_dday()
        show_everyday()
        
def show_dday():
    if os.path.exists(dday_path):
        with open('ddaylist.pickle', 'rb') as f:
            ddaylist = pickle.load(f)

            print(" ----------- D-day Todo List -----------------------------------------------------------------")
            for k,v in ddaylist.items():
                print("|{:<11} | {:<80}|".format(k,v))
            print(" ---------------------------------------------------------------------------------------------")
    else:
        print("You need to add <D-day Todo List> first")
        return
    
    
def show_everyday():
    if os.path.exists(everyday_path):
        with open('everydaylist.pickle', 'rb') as f:
            everydaylist = pickle.load(f)

            print(" ----------- Everyday Todo List --------------------------------------------------------------")
            for i,v in enumerate(everydaylist):
                print("|{:^4}| {:<88}|".format(i+1,v))
            print(" ---------------------------------------------------------------------------------------------")
    else:
        print("You need to add <Everyday Todo List> first")
        return
    

def add_dday(dday):
    if os.path.exists(dday_path):
        with open('ddaylist.pickle', 'rb') as f:
            ddaylist = pickle.load(f)
            print("Current D-day Todo List")
            show_dday()
    else:
        print("New D-day List")
        ddaylist={}

    if dday in ddaylist: # 중복 날짜 있으면
        print("Same d-day date!!")
        count = 2
        new_dday = f"{dday}({count})"
        while new_dday in ddaylist:
            count +=1
            new_dday = f"{dday}({count})"
        print(f"\'{dday}\' changed to \'{new_dday}\'")
        
    else: # 중복 없으면
        new_dday = dday

    content = input("Enter your content: ")
    ddaylist[new_dday] = content

    #sort by dday
    sorted_ddaylist =dict(sorted(ddaylist.items()))

    with open('ddaylist.pickle', 'wb') as f:
        pickle.dump(sorted_ddaylist, f)

    return

def add_everyday(ordernum):
    index = int(ordernum)-1

    if os.path.exists(everyday_path):
        with open('everydaylist.pickle', 'rb') as f:
            everydaylist = pickle.load(f)
            print("Current Everyday Todo List")
            show_everyday()
    else:
        print("New Everyday List")
        everydaylist=[]

    if index < len(everydaylist):
        print("Order will be changed")
        content = input("Enter your content: ")
        everydaylist.insert(index, content)
    else:
        content = input("Enter your content: ")
        everydaylist.append(content)

    with open('everydaylist.pickle', 'wb') as f:
        pickle.dump(everydaylist, f)
  
    return

def del_dday(dday):
    if os.path.exists(dday_path):
        with open('ddaylist.pickle', 'rb') as f:
            ddaylist = pickle.load(f)
    else:
        print("No <D-day Todo List> to delete")
        return 
    
    if dday in ddaylist: 
        del ddaylist[dday]
        if not ddaylist: # ddaylist 비어있으면 파일 삭제
            print("File will be deleted")
            os.remove(dday_path)
            return
    else:
        print(f"Fail to search {dday} todo")

    #sort by dday
    sorted_ddaylist =dict(sorted(ddaylist.items()))

    with open('ddaylist.pickle', 'wb') as f:
        pickle.dump(sorted_ddaylist, f)

    print(f"{dday} Deleted")

    return


def del_everyday(ordernum):
    if os.path.exists(everyday_path):
        with open('everydaylist.pickle', 'rb') as f:
            everydaylist = pickle.load(f)
    else:
        print("No <Everyday Todo List> to delete")
        return 
    
    index = int(ordernum)-1

    if index < len(everydaylist):
        del everydaylist[index]
        if len(everydaylist) == 0: # everydaylist 비어있으면 파일 삭제
            print("File will be deleted")
            os.remove(everyday_path)
            return
    else:
        print(f"Wrong order number")
        return

    with open('everydaylist.pickle', 'wb') as f:
        pickle.dump(everydaylist, f)
    print(f"{ordernum} Deleted")
    return

def main():
        
    parser = argparse.ArgumentParser(description="Todo List CLI")
    subparsers = parser.add_subparsers(dest="menu")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("--todo", type = str, choices=['dday','everyday','all'])

    add_parser = subparsers.add_parser("adddday")
    add_parser.add_argument("--dday", required=True, type = str, help="YY-MM-DD")

    add_parser = subparsers.add_parser("addeveryday")
    add_parser.add_argument("--ordernum", required=True, type = str, help = "order number")

    add_parser = subparsers.add_parser("deldday")
    add_parser.add_argument("--dday", required=True, type = str, help="YY-MM-DD")

    add_parser = subparsers.add_parser("deleveryday")
    add_parser.add_argument("--ordernum", required=True, type = str, help = "order number")

    args = parser.parse_args()

    if args.menu == 'show':
        show_list(args.todo)
    elif args.menu == 'adddday':
        add_dday(args.dday)
    elif args.menu == 'addeveryday':
        add_everyday(args.ordernum)
    elif args.menu == 'deldday':
        del_dday(args.dday)
    elif args.menu == 'deleveryday':
        del_everyday(args.ordernum)


if __name__ == "__main__":
    main()
