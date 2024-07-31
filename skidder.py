import socket, subprocess, threading, time

PS1         = "[Skidder@Net] # ~ ";
DB_PATH     = "assets/db/users.db";
BUFF_SZ     = 1024;

class User():
    name:       str = "";
    ip_addr:    str = "";
    passwd:     str = "";
    plan:       int = 0;
    max_con:    int = 0;
    max_time:   int = 0;
    curr_con:   int = 0;
    rank:       int = 0;
    expiry:     str = "";
    def __init__(self, arr: list[str]) -> None:
        if len(arr) != 9:
            return
        
        self.name = arr[0]; self.ip_addr = arr[1]; self.passwd = arr[2];
        self.plan = int(arr[3]); self.max_con = int(arr[4]); 
        self.max_time = int(arr[5]); self.curr_con = int(arr[6]); 
        self.rank = int(arr[7]); self.expiry = arr[8]
        

class SkidderNet():
    __Socket:       socket.socket;
    __Interface:    str = "";
    __InterfaceIP:  str = "";
    __Users:        list[User];
    def __init__(self, port: int) -> None:
        self.__Interface = self.__getInterface()
        self.__InterfaceIP = self.__getInterfaceIP()
        self.__Users = []
        print("[ + ] Loading user db....!")
        db = open(DB_PATH, "r")
        if not db:
            print("[ x ] User db is missing!")
            exit(0)

        db_data = db.read()
        lines = db_data.replace("(", "").replace(")", "").replace("'", "").split("\n")
        for line in lines:
            if len(line) < 3 or "USERNAME" in line: continue
            args = line.split(",")
            if len(args) != 9:
                print("Corrupted User Line In DB....!")
                exit(0)

            self.__Users.append(User(args))

        print(f"[ + ] Users loaded....!")

        self.__Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.__Socket.bind(("0.0.0.0", port));
    
        self.__Socket.listen(99)
        self.__IncomingReqEvent = None
        self.__SuccessLoginEvent = None
        self.__FailedLoginEvent = None
        self.__InputEvent = None
        self.__DisconnectEvent = None
        print(f"[ + ] Socket server has started....!")

    """
        SkidderNet Connection Handler
    """

    def ConnectionListener(self) -> None:
        while True:
            client, addr = self.__Socket.accept()

            threading.Thread(target=self.AuthorizeConnection, args=(client, )).start()

            
    def AuthorizeConnection(self, client) -> None:
        if self.__IncomingReqEvent:
            self.__IncomingReqEvent(client)

        client.send("Username: ".encode())
        user        = client.recv(BUFF_SZ).decode().strip().replace("\r", "").replace("\n", "")
        client.send("Password: ".encode())
        passwd      = client.recv(BUFF_SZ).decode().strip().replace("\r", "").replace("\n", "")
        if passwd == "":
            passwd      = client.recv(BUFF_SZ).decode().strip().replace("\r", "").replace("\n", "")

        get_info = self.findUser(user)
        if get_info.name == user and get_info.passwd == passwd:
            if self.__SuccessLoginEvent:
                self.__SuccessLoginEvent(client, get_info)
            
            print("HERE 1")
            self.HandleCLI(client, get_info)
            print("HERE 2")
        else:
            if self.__FailedLoginEvent:
                self.__FailedLoginEvent(client)

    def HandleCLI(self, client, user) -> None:
        print("HERE 3")
        global PS1
        while True:
            client.send(PS1.encode())
            data = client.recv(BUFF_SZ).decode().strip().replace("\r", "").replace("\n", "")

            if not data or len(data) < 3:
                continue


            if self.__InputEvent:
                self.__InputEvent(client, user, data)

            elif data == "test":
                client.send("Working\r\n".encode())
            
            client.send(PS1.encode())

    """
        Event Method Linking
    """

    def LoadIncomingReqEvent(self, method) -> None:
        self.__IncomingReqEvent = method
        print("[ SKIDDER ] IncomingReqEvent Linked")

    def LoadLoginEvent(self, success_login, failed_login) -> None:
        self.__SuccessLoginEvent = success_login;
        self.__FailedLoginEvent = failed_login;
        print("[ SKIDDER ] SuccessLoginEvent and FailedLoginEvent Linked")

    def LoadInputEvent(self, handler) -> None:
        self.__InputEvent = handler
        print("[ SKIDDER ] InputEvent Linked")

    """
        Crud && User Utils
    """
    
    def findUser(self, username: str) -> User:
        for user in self.__Users:
            if user.name == username:
                return user;

        return None;


    """
        System Utils Methods
    """

    def __getInterface(self) -> str:
        data = subprocess.getoutput("ifconfig");
        lines = data.split("\n")

        for line in lines:
            if line.startswith(" ") == False and ":" in line:
                return line.split(" ")[0].replace(":", "");
            
        return "";

    def __getInterfaceIP(self) -> str:
        data = subprocess.getoutput("ifconfig");
        lines = data.split("\n")
        
        i = 0
        for line in lines:
            if self.__Interface in line:
                return lines[i + 1].split(" ")[1];
            
            i += 1

        return ""; 
