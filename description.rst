.. _lib_ubitool_descreiption:

===================================================================================================
ubitool
===================================================================================================

---------------------------------------------------------------------------------------------
개요
---------------------------------------------------------------------------------------------

ubitool은 ubinos를 위한 다목적 도구 모음입니다.

----------------------------------------------------------------------------------------------
기본 정보
----------------------------------------------------------------------------------------------

.. code-block:: yaml

    type: python_app
    main_file: lib/ubitool/main.py
    tmux_session:
        debug:
            name: appcon2
        console: 
            name: appcon2

---------------------------------------------------------------------------------------------
주요 기능
---------------------------------------------------------------------------------------------

* 파일의 마지막 부분 출력 (tail)
* 파일의 읽지 않은 부분만 출력 (htail - history tail)
* tmux session 로그 확인 (shtail - tmux session history tail)
* tmux session 에 키 전송 (ssend - tmux session send key)
* 기대 문자열이 나올 때까지 tmux 세션에 키 전송 반복 실행 (stssend - strict ssend).
* 쉘 명령어 실행 및 결과 출력 (shell)
* 기대 문자열이 나올 때까지 쉘 명령어 반복 실행 (stshell - strict shell)
* 디렉토리 내용 및 파일 패턴 출력 (ls) - 와일드카드 지원
* 파일 또는 stdin 입력 줄 정렬 (sort) - 파이프 연산 지원

---------------------------------------------------------------------------------------------
구현 세부사항
---------------------------------------------------------------------------------------------

* **Parameter 처리**: Typer 라이브러리 사용 (타입 힌트 기반 CLI 프레임워크)
* **json command 구현**: json5, jmespath 라이브러리를 사용하고, 주석도 허용
* **Debug 모드**: ipdb 라이브러리 사용 (대화형 Python 디버거)
* 다음 오류가 발생하지 않게 작성해야 합니다.
    .. code-block:: 

        'utf-8' codec can't decode byte 0xaa in position 9647738: invalid start byte

* Command 별로 source file 을 분리해주세요.
* 시험용 file 은 아래 디렉토리에 있는 것들을 사용해주세요. 없다면 여기에 만들어 주세요.
    + lib/ubitool/test_data

---------------------------------------------------------------------------------------------
설치 방법
---------------------------------------------------------------------------------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pip를 통한 설치
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ubitool은 pip를 통해 설치할 수 있습니다:

.. code-block:: bash

    # 개발 모드로 설치 (소스 코드 변경 시 자동 반영)
    pip install -e lib/ubitool

    # 일반 설치
    pip install lib/ubitool

설치 후 시스템 어디서나 ``ubitool`` 명령어를 사용할 수 있습니다:

.. code-block:: bash

    ubitool --help
    ubitool --version

---------------------------------------------------------------------------------------------
사용법
---------------------------------------------------------------------------------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
기본 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool [OPTIONS] COMMAND [ARGS]...

        ubitool is a toolbox for ubinos.

    Options:
        -h, --help      Show this message and exit.
        -v, --version   Show the version and exit.
        -d, --debug     Enable debug mode (interactive debugging with ipdb).

    Commands:
        tail            Print the last part of a file.
        htail           Print the unread portion of a file (with position tracking).
        shtail          Execute htail on the latest tmux session log file.
        ssend           Send keys to tmux session.
        stssend         Retry sending keys to tmux session (strict ssend).
        shell           Execute a shell command and display the output.
        stshell         Retry shell command until expected result appears (strict shell).
        ls              List directory contents or files matching patterns.
        sort            Sort lines of text file or stdin input.
        json            Read or write json file.
        libmgr          Launch library manager

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
libmgr 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool libmgr [OPTIONS]

        Laungh library manager.

    Options:
        -h, --help              Show this message and exit.
        -b, --base-path TEXT    Base path
                                [default: .]
        -l, --lib-path TEXT     Library relative path
                                [default: lib]
        -f, --list-file TEXT    Library list file relative path
                                [default: liblist.json]

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
json 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool json [OPTIONS] FILE

        Print or write json file.

    Arguments:
        FILE    Path to the json target file.  [required]

    Options:
        -h, --help           Show this message and exit.
        -r, --read           Print the value of a specified key of the json target file (requires --key)
        -w, --write          Write a specified value to a specified key of the json target file (requires --key and --value)
        -k, --key TEXT       Specify a key
        -v, --value TEXT     Specify a value

    Examples:
        # Read the value of "C_Cpp.default.compileCommands" key
        ubitool json -r -k "[\"C_Cpp.default.compileCommands\"]" .vscode/settings.json

        # Write "./compile_commands.json" to "C_Cpp.default.compileCommands" key
        ubitool json -w -k "[\"C_Cpp.default.compileCommands\"]" -v "./compile_commands.json" .vscode/settings.json

        # Read the value of "git.detectSubmodulesLimit" key
        ubitool json -r -k "[\"git.detectSubmodulesLimit\"]" .vscode/settings.json

        # Write 120 to "git.detectSubmodulesLimit" key
        ubitool json -w -k "[\"git.detectSubmodulesLimit\"]" -v 120 .vscode/settings.json

        # Read the value of "configurations[?name==\"target app debug\"].cwd | [0]" key
        ubitool json -r -k "configurations[?name==\"target app debug\"].cwd | [0]" .vscode/launch.json

        # Write "" of "configurations[?name==\"target app debug\"].cwd | [0]" key
        ubitool json -w -k "configurations[?name==\"target app debug\"].cwd | [0]" -v "./build/pico_hi_world" .vscode/launch.json

        # Read the value of "tasks[?label==\"target app reset\"].options.cwd | [0]" key
        ubitool json -r -k "tasks[?label==\"target app reset\"].options.cwd | [0]" .vscode/tasks.json

        # Write "" of "tasks[?label==\"target app reset\"].options.cwd | [0]" key
        ubitool json -w -k "tasks[?label==\"target app reset\"].options.cwd | [0]" -v "./build/pico_hi_world" .vscode/tasks.json

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tail 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool tail [OPTIONS] FILE

        Print the last part of a file.

    Arguments:
        FILE  Path to the file to read.  [required]

    Options:
        -h, --help          Show this message and exit.
        -n, --lines INTEGER Number of lines to display from the end of the file.
                            [default: 10]
        -c, --bytes INTEGER Number of bytes to display from the end of the file.
                            (Overrides -n if both specified)

    Examples:
        ubitool tail /var/log/syslog              # Show last 10 lines
        ubitool tail -n 20 /var/log/syslog        # Show last 20 lines
        ubitool tail -c 1024 /var/log/syslog      # Show last 1024 bytes

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
htail 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool htail [OPTIONS] FILE

        Print the unread portion of a file since last access.

        This command tracks the reading position and only displays new content
        added since the last read. The position is saved in a hidden file
        (.FILE.htail) in the same directory as the target file.

    Arguments:
        FILE  Path to the file to read.  [required]

    Options:
        -h, --help          Show this message and exit.
        -n, --lines INTEGER Maximum number of new lines to display.
                            [default: 10]
        -c, --bytes INTEGER Maximum number of new bytes to display.
                            (Overrides -n if both specified)
        --keep              Do not update last read position.
        --reset             Reset the saved position and read from the beginning.
        --last              Mark current end of file as read (skip to end without displaying).

    Examples:
        ubitool htail /var/log/app.log                   # Show new content since last read
        ubitool htail -n 50 /var/log/app.log             # Show max 50 new lines
        ubitool htail -n 50 --keep /var/log/app.log      # Show max 50 new lines without updating position
        ubitool htail --reset /var/log/app.log           # Reset position and read from start
        ubitool htail --last /var/log/app.log            # Mark all as read, skip to end

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
shtail 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool shtail [OPTIONS] PATH

        Execute htail on the latest tmux session log file.

        Finds and reads the latest log file matching the pattern:
        PATH/session_<target-session>_window_0_pane_0_*.log

    Arguments:
        PATH  Directory containing tmux log files.  [default: ~/Workspace/log/tmux]

    Options:
        -h, --help                  Show this message and exit.
        -t, --target-session TEXT   Target tmux session name.  [required]
        -n, --lines INTEGER         Maximum number of new lines to display.
                                    [default: 10]
        -c, --bytes INTEGER         Maximum number of new bytes to display.
                                    (Overrides -n if both specified)
        --keep                      Do not update last read position.
        --reset                     Reset the saved position and read from the beginning.
        --last                      Mark current end of file as read (skip to end without displaying).

    Examples:
        ubitool shtail -t build1 ~/Workspace/log/tmux         # Show new content since last read
        ubitool shtail -t dev -n 50 /var/log/tmux             # Show max 50 new lines
        ubitool shtail -t test --reset ~/log                  # Reset and read from start
        ubitool shtail -t prod --last ~/Workspace/log/tmux    # Mark all as read

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ssend 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool ssend [OPTIONS] KEYS

        Send keys through tmux session

    Arguments:
        KEYS  Keys to send.  [required]

    Options:
        -h, --help                  Show this message and exit.
        -t, --target-session TEXT   Target tmux session name.  [required]

    Examples:
        ubitool ssend -t build1 "pwd" Enter   # Same as tmux send-keys -t build1 "pwd" Enter

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
stssend 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool stssend [OPTIONS] KEYS

        Retry sending keys through tmux session (strict ssend).

        This command repeatedly sends keys until the output
        contains the expected string or the retry limit is reached.

        Output is get with the shtail command logic
        
        After send cancel key and before resend KEYS, output should be cleared with htail command logic.

    Arguments:
        KEYS  Keys to send.  [required]

    Options:
        -h, --help                  Show this message and exit.
        -t, --target-session TEXT   Target tmux session name.  [required]
        -o, --output-path PATH      Directory containing tmux log files.
                                    Finds and reads the latest log file matching the pattern:
                                    PATH/session_<target-session>_window_0_pane_0_*.log
                                    [default: ~/Workspace/log/tmux]
        -e, --expect TEXT           Expected string in the output.  [required]
        -r, --retry INTEGER         Maximum number of retries.
                                    [default: 10]
        --retry-interval INTEGER    Interval between retries in seconds.
                                    [default: 1]
        --timeout INTEGER           Timeout for each command execution in seconds.
                                    [default: 30]
        -c, --cancel-key TEXT       Key sent before every retry to cancel the previous one.

    Examples:
        ubitool stssend -t build1 -o ~/Workspace/ubinos/ubiworks/log/tmux -e "ready" "systemctl status myservice" Enter
        ubitool stssend -t build1 -o ~/Workspace/ubinos/ubiworks/log/tmux -e "connected" -r 20 "ping -c 1 server.com" Enter
        ubitool stssend -t build1 -o ~/Workspace/ubinos/ubiworks/log/tmux -e "active" --timeout 5 "systemctl is-active myservice" Enter
        ubitool stssend -t build1 -o ~/Workspace/ubinos/ubiworks/log/tmux -e "ready" --retry-interval 5 "systemctl status myservice" Enter
        ubitool stssend -t build1 -o ~/Workspace/ubinos/ubiworks_cmake/log/tmux --expect "$ " --timeout 30 -c C-c -c "q" -c Enter -c "y" -c Enter "make load" Enter

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
shell 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool shell [OPTIONS] COMMAND

        Execute a shell command and display the output.

    Arguments:
        COMMAND  Shell command to execute (use quotes for complex commands).  [required]

    Options:
        -h, --help              Show this message and exit.
        --timeout INTEGER       Command execution timeout in seconds.
                                [default: 30]
        --capture-stderr        Capture and display stderr output as well.

    Examples:
        ubitool shell "ls -la"                    # List files
        ubitool shell "ps aux | grep python"      # Complex command with pipe
        ubitool shell --timeout 5 "sleep 10"      # Command with timeout

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
stshell 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool stshell [OPTIONS] COMMAND

        Retry shell command until expected result appears (strict shell).

        This command repeatedly executes a shell command until the output
        contains the expected string or the retry limit is reached.

    Arguments:
        COMMAND  Shell command to execute (use quotes for complex commands).  [required]

    Options:
        -h, --help                  Show this message and exit.
        --expect TEXT               Expected string in the output.  [required]
        --retry INTEGER             Maximum number of retries.
                                    [default: 10]
        --retry-interval INTEGER    Interval between retries in seconds.
                                    [default: 1]
        --timeout INTEGER           Timeout for each command execution in seconds.
                                    [default: 30]
        --capture-stderr            Capture and display stderr output as well.

    Examples:
        ubitool stshell --expect "ready" "systemctl status myservice"
        ubitool stshell --expect "connected" --retry 20 "ping -c 1 server.com"
        ubitool stshell --expect "active" --timeout 5 "systemctl is-active myservice"
        ubitool stshell --expect "error" --capture-stderr "ls nonexistent_file"
        ubitool stshell --expect "ready" --retry-interval 5 "systemctl status myservice"

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ls 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool ls [OPTIONS] [PATHS]...

        List directory contents or files matching patterns.

    Arguments:
        PATHS  Paths to list (files or directories). Can include wildcards/patterns.
               Defaults to current directory if none specified.
               [default: None]

    Options:
        -h, --help  Show this message and exit.
        -a, --all   Include entries starting with dot (.)

    Examples:
        ubitool ls                                # List current directory
        ubitool ls -a ./test                      # List all entries in ./test
        ubitool ls ./test/test_*_file.log         # List matching files in ./test
        ubitool ls "*.txt"                        # List all .txt files in current directory
        ubitool ls "subdir*"                      # List all items starting with 'subdir'

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sort 명령어
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    Usage: ubitool sort [OPTIONS] [FILE]

        Sort lines of text file or stdin input.

    Arguments:
        FILE  File to sort. If not provided, reads from stdin.  [optional]

    Options:
        -h, --help          Show this message and exit.
        -r, --reverse       Reverse the result of comparisons.

    Examples:
        ubitool sort test.txt                     # Sort lines in ascending order
        ubitool sort -r test.txt                  # Sort lines in descending order
        ubitool ls | ubitool sort                 # Sort output from ls command
        ubitool ls "*.txt" | ubitool sort -r      # Sort ls output in reverse order

---------------------------------------------------------------------------------------------
사용 예제
---------------------------------------------------------------------------------------------

.. code-block:: bash

    # 로그 파일의 마지막 20줄 확인
    ubitool tail -n 20 /var/log/application.log

    # 새로운 로그 항목만 확인 (이전 읽기 위치부터)
    ubitool htail /var/log/application.log

    # tmux 세션 로그 확인 (새로운 내용만)
    ubitool shtail -t build1 ~/Workspace/log/tmux

    # tmux 세션 로그 50줄 확인
    ubitool shtail -t dev -n 50 ~/Workspace/log/tmux

    # tmux 세션에 명령어 전송
    ubitool ssend -t build1 "pwd" Enter

    # tmux 세션에 명령어 전송하고 결과 대기
    ubitool stssend -t build1 --expect "ready" "systemctl status myservice"

    # 시스템 정보 확인
    ubitool shell "uname -a"

    # 서비스가 준비될 때까지 대기
    ubitool stshell --expect "active" "systemctl is-active myservice"

    # 네트워크 연결 확인 (최대 20번 재시도)
    ubitool stshell --expect "connected" --retry 20 "ping -c 1 google.com"

    # 에러 메시지 확인 (stderr 포함)
    ubitool stshell --expect "not found" --capture-stderr "ls nonexistent"

    # 긴 간격으로 서비스 상태 확인 (5초 간격)
    ubitool stshell --expect "active" --retry-interval 5 "systemctl is-active myservice"

    # 현재 디렉토리 내용 확인
    ubitool ls -a

    # 특정 패턴의 파일들 확인
    ubitool ls "*.txt"

    # 로그 파일 정렬
    ubitool sort /var/log/application.log

    # 파이프를 이용한 디렉토리 내용 정렬
    ubitool ls | ubitool sort

    # 와일드카드와 파이프를 함께 사용
    ubitool ls "*.log" | ubitool sort -r

    # 디버그 모드로 실행
    ubitool -d tail /var/log/application.log

---------------------------------------------------------------------------------------------
주의사항
---------------------------------------------------------------------------------------------

* htail 명령어는 읽기 위치를 `.FILE.htail` 파일에 저장합니다 (동일 디렉토리에 쓰기 권한 필요).
* shtail 명령어는 tmux 로그 파일 명명 규칙(session_<name>_window_0_pane_0_*.log)을 따르는 파일을 찾습니다.
     + 여러 로그 파일이 있을 경우 shtail은 가장 최신 파일을 자동으로 선택합니다.
* shell 및 stshell 명령어는 시스템 쉘에서 직접 실행되므로 신뢰할 수 없는 입력에 주의하세요.
* stshell 명령어는 기본적으로 재시도 간격으로 1초 대기하며, --retry-interval 옵션으로 조정 가능합니다.
* stshell 명령어는 각 시도마다 진행 상황을 출력합니다.
* 여러 프로세스가 동시에 같은 파일을 htail로 읽으면 위치 파일이 충돌할 수 있습니다.
* ls 명령어에서 와일드카드 사용 시 쉘이 아닌 Python glob 패턴이 적용됩니다.
* sort 명령어는 파일 인수가 없으면 stdin에서 입력을 읽어 파이프 연산을 지원합니다.

---------------------------------------------------------------------------------------------
파이프 연산 지원
---------------------------------------------------------------------------------------------

ubitool 의 ls 와 sort 명령어는 파이프 연산을 지원합니다:

.. code-block:: bash

    # ls 출력을 sort로 정렬
    ubitool ls | ubitool sort

    # 와일드카드 패턴과 역순 정렬 조합
    ubitool ls "*.txt" | ubitool sort -r

    # 숨김 파일 포함하여 정렬
    ubitool ls -a | ubitool sort

---------------------------------------------------------------------------------------------
stshell 명령어 상세 동작
---------------------------------------------------------------------------------------------

stshell 명령어는 다음과 같은 방식으로 동작합니다:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
재시도 메커니즘
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* 각 시도마다 "Attempt X/Y" 형태로 진행 상황 출력
* 예상 문자열이 발견되지 않으면 설정된 간격(기본 1초) 대기 후 재시도
* --retry-interval 옵션으로 재시도 간격 조정 가능 (0초부터 임의 초까지)
* 모든 재시도 실패 시 exit code 1로 종료
* 성공 시 "Success: Expected string 'XXX' found" 메시지 출력

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
출력 처리
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* 기본적으로 stdout만 캡처하여 예상 문자열 검색
* --capture-stderr 옵션 사용 시 stderr도 함께 캡처 및 검색
* 각 시도의 명령어 출력을 실시간으로 표시
* 타임아웃 발생 시 "Command timed out" 메시지 출력

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
사용 시나리오
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* 서비스 상태 모니터링: 서비스가 활성화될 때까지 대기
* 네트워크 연결 확인: 연결이 성공할 때까지 반복 시도
* 파일 생성 대기: 특정 파일이 생성될 때까지 모니터링
* 로그 메시지 대기: 특정 로그 메시지가 나타날 때까지 확인

---------------------------------------------------------------------------------------------
shtail 명령어 상세 동작
---------------------------------------------------------------------------------------------

shtail은 tmux 세션 로그를 효율적으로 확인하기 위한 특수 명령어입니다:

* 지정된 디렉토리에서 패턴 매칭으로 로그 파일 검색
* 타임스탬프 기반으로 가장 최신 로그 파일 자동 선택
* htail의 모든 기능을 tmux 로그에 특화하여 제공
* 세션별 읽기 위치 독립 관리
