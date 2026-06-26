#!/bin/sh

ALLOWED_PORT_LETTERS="A B C"

usage() {
    ALLOWED_PORT_LETTERS_LIST=$(echo "$ALLOWED_PORT_LETTERS" | sed 's/ /|/g')

    echo "Использование: $0 [опции]"
    echo ""
    echo "Опции:"
    echo "  -b, --booten                     Включить режим booten"
    echo "      --booten_port_letter <${ALLOWED_PORT_LETTERS_LIST}> Указать букву порта для booten"
    echo "      --booten_port_number <0-15>  Указать номер порта для booten"
    echo "  -d, --debug                      Включить режим debug"
    echo "      --debug_port_letter <${ALLOWED_PORT_LETTERS_LIST}>  Указать букву порта для debug"
    echo "      --debug_port_number <0-15>   Указать номер порта для debug"
    echo "      --uart_timeout <мс>          Таймаут UART в миллисекундах"
    echo "  -h, --help                       Показать эту справку"
    echo ""
    exit 0
}
cd k1921vg015-flasher


OPTIONS=bdh
LONGOPTS=booten,debug,help,booten_port_letter:,booten_port_number:,debug_port_letter:,debug_port_number:,uart_timeout:

PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [ $? -ne 0 ]; then
    exit 2
fi

eval set -- "$PARSED"

booten=
debug=
booten_port_letter=
booten_port_number=
debug_port_letter=
debug_port_number=
uart_timeout=

while true; do
    case "$1" in
        -b|--booten) booten=1; shift ;;
        -d|--debug) debug=1; shift ;;
        -h|--help) usage; exit 0 ;;
        --booten_port_letter) booten_port_letter="$2"; shift 2 ;;
        --booten_port_number) booten_port_number="$2"; shift 2 ;;
        --debug_port_letter) debug_port_letter="$2"; shift 2 ;;
        --debug_port_number) debug_port_number="$2"; shift 2 ;;
        --uart_timeout) uart_timeout="$2"; shift 2 ;;
        --) shift; break ;;
        *) echo "Неизвестная опция: $1" >&2; exit 3 ;;
    esac
done

validate_port_letter() {
    local letter="$1"
    for allowed in $ALLOWED_PORT_LETTERS; do
        if [ "$letter" = "$allowed" ]; then
            return 0
        fi
    done
    return 1
}

validate_port_number() {
    local number="$1"
    if echo "$number" | grep -Eq '^[0-9]+$' && [ "$number" -ge 0 ] && [ "$number" -le 15 ]; then
        return 0
    else
        return 1
    fi
}

if [ -n "$booten_port_letter" ] && ! validate_port_letter "$booten_port_letter"; then
    echo "Ошибка: booten_port_letter должен быть одним из: $ALLOWED_PORT_LETTERS"
    exit 4
fi

if [ -n "$debug_port_letter" ] && ! validate_port_letter "$debug_port_letter"; then
    echo "Ошибка: debug_port_letter должен быть одним из: $ALLOWED_PORT_LETTERS"
    exit 5
fi

if [ -n "$booten_port_number" ] && ! validate_port_number "$booten_port_number"; then
    echo "Ошибка: booten_port_number должен быть числом от 0 до 15"
    exit 6
fi

if [ -n "$debug_port_number" ] && ! validate_port_number "$debug_port_number"; then
    echo "Ошибка: debug_port_number должен быть числом от 0 до 15"
    exit 7
fi


ADDITIONAL_FLAGS=""

[ -n "$booten_port_letter" ]   && ADDITIONAL_FLAGS="$ADDITIONAL_FLAGS -DBOOTEN_PORT_LETTER=$booten_port_letter"
[ -n "$booten_port_number" ]   && ADDITIONAL_FLAGS="$ADDITIONAL_FLAGS -DBOOTEN_PORT_NUMBER=$booten_port_number"
[ -n "$debug_port_letter" ]    && ADDITIONAL_FLAGS="$ADDITIONAL_FLAGS -DDEBUG_PORT_LETTER=$debug_port_letter"
[ -n "$debug_port_number" ]    && ADDITIONAL_FLAGS="$ADDITIONAL_FLAGS -DDEBUG_PORT_NUMBER=$debug_port_number"
[ -n "$uart_timeout" ]         && ADDITIONAL_FLAGS="$ADDITIONAL_FLAGS -DUART_TIMEOUT=$uart_timeout"

make all BUILD_PATH=../build ADDITIONAL_FLAGS="$ADDITIONAL_FLAGS"
