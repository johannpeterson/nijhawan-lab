export FG_BLACK=$(tput setaf 0)
export FG_RED=$(tput setaf 1)
export FG_GREEN=$(tput setaf 2)
export FG_YELLOW=$(tput setaf 3)
export FG_BLUE=$(tput setaf 4)
export FG_MAGENTA=$(tput setaf 5)
export FG_CYAN=$(tput setaf 6)
export FG_WHITE=$(tput setaf 7)
export FG_DEFAULT=$(tput setaf 9)

export BG_BLACK=$(tput setab 0)
export BG_RED=$(tput setab 1)
export BG_GREEN=$(tput setab 2)
export BG_YELLOW=$(tput setab 3)
export BG_BLUE=$(tput setab 4)
export BG_MAGENTA=$(tput setab 5)
export BG_CYAN=$(tput setab 6)
export BG_WHITE=$(tput setab 7)
export BG_DEFAULT=$(tput setab 9)

export BOLD=$(tput bold)
export UNDERLINE_ON=$(tput smul)
export UNDERLINE_OFF=$(tput rmul)
export ALL_OFF=$(tput sgr0)

tput_color_test() {
    # tput_colors - Demonstrate color combinations.
    default_background=$(tput setab 0)
    
    for fg_color in {0..7}; do
        set_foreground=$(tput setaf $fg_color)
        for bg_color in {0..7}; do
            set_background=$(tput setab $bg_color)
            echo -n $set_background$set_foreground
            printf ' F:%s B:%s ' $fg_color $bg_color
        done
        echo $default_background
    done
    echo $(tput sgr0)
}

tput_face_test() {
    tput sgr0; echo "normal"; tput_color_test;
    
    tput bold; echo "bold"; tput_color_test; tput sgr0

    tput smul; echo "underline"; tput_color_test; tput rmul

    # Most terminal emulators do not support blinking text (though xterm
    # does) because blinking text is considered to be in bad taste ;-)
    tput blink; echo "blink"; tput_color_test; tput sgr0

    tput rev; echo "reverse"; tput_color_test;  tput sgr0

    # Standout mode is reverse on many terminals, bold on others. 
    tput smso; echo "stand-out"; tput_color_test; tput rmso

    tput sgr0
}
