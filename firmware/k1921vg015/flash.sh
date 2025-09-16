#!/bin/bash

usage() {
    echo "Использование: $0 [опции]"
    echo "  -h, --help           Показать эту справку"
    echo "  -o, --openocd-path   Указать путь к openocd"
    exit 0
}

OPENOCD_PATH="openocd"

OPTIONS="ho:"
LONGOPTS="openocd-path:,help"

PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [ $? -ne 0 ]; then
    echo "Ошибка при разборе параметров." >&2
    exit 1
fi

eval set -- "$PARSED"

while true; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -o|--openocd-path)
            OPENOCD_PATH="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Неизвестная опция: $1" >&2
            exit 2
            ;;
    esac
done

if ! command -v "$OPENOCD_PATH" &> /dev/null; then
    echo "Ошибка: Не удалось найти openocd по пути $OPENOCD_PATH" >&2
    exit 3
fi

if ! [ -e "./build/k1921vg015_flasher.elf" ]; then
    read -p "Enter y to build program" user_input
    if [[ "$user_input" == "y" || "$user_input" == "Y" ]]; then
        ./build.sh
    else 
        exit 4
    fi
fi

$OPENOCD_PATH -s ./init -f onboard_ftdi.cfg -f k1921vg015.cfg -c "program ./build/k1921vg015_flasher.elf reset exit"
