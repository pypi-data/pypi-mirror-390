from random import choice, seed
import random
import json
import time
import os


holy_img = """
                                            ;@#@@$|;'`.                                            
                                            ;@#############&|:`                                    
                                            ;@####################|`                               
                                            ;@####################@@##$:                           
                                            :@#@#########################@!.                       
                                      .%####$;::;$###########################|.                    
                                      .%####|    |#############################&:                  
                       .;&#%.         .%####|    |###########$!$##################|.               
                    '&##@##@$`        `%####|    |#@@#######%.    '$################|              
                 `%##########&: `:|&########|     .`:%#####%.        `$##############@;            
                  :&#############@@#########|                       .%###############@@$'          
                   '$#######################|                      .|###################@!.        
                    `$#############@########%.                    .|######################$`       
                   !##############@|'       :@#####&!'             .!@#####################&`      
       .%@;.     |#############%`           ;######@@###$`            ;@##################@@&'     
      :&#####&:|##########@#&:              ;@#############$.           ;@#&;`   |###########&:    
     |########@###########&'                :@#############@#$`                   '&##########&'   
    !####################|.                 :@################@;                   '&##########$`  
   ;@@@#################!                   :@##################|                   ;@##########|  
     '$@###############!                    :@##################@;               ;&#############@: 
        .%############$`                    :@###################$`           `$#@###############%.
        `$############|                     :@###################&'            |#################@:'
        |#############|                     :@###################@:            '&#################|:
       `$#############|.                    :@###################&'             |#################$!
   ...`%##############&'                    :@#################@#%.             '$################@%
&######################$.                   :@##################&:                      |##########$
&#######################|                   :@#################@;                       ;@#########$
&#######################@:                  :@#################%.                       :@#########$
&########################|                  ;@#################!                        !##########$
@########################|                  ;@#########@@@@#@#@;                       `%##########$
       ;@###############$`    `::`          :@####@@###$:';&###&'               '&################@%
       .%##############|    `$#@@###$;`.    ;@@##&|:        ;@##@:             .%#################$!
        !#############&:    `$#######@@@#%. :@@;            |####|.            ;@#################|'
        .%#############&:    :@#@@@##@%'    :@##@!`        '$#@@%`            .%#################@:'
        :$##############&:    .::`.        :;;&######@%!:;$##@@%.             '$#################%.
    .;@##################|                ;@! `&######@@#@#####!                 '%##@##########&: 
   '&@@###################!              `$#!  !#########@#@@#|                     |###########|  
    :@#####################&!'`:!|'      '' :@$!&#####$``;!;'                      ;@##########$`  
     :@#####################@#@@#|          ;&@########|                          |###########&'   
      `$#@##@|.'%#############@#$`          ;@########@$'              '%###$'  .%###########&:    
       .|$:      '$#############%.       .  ;@#$|&##@@#&:            `$#####################&'     
                   `%###########!  .'.  |!  ;##%:%#&;$##|          '$######################&'      
                    '$######################|.                     ;######################%.       
                   |########################|.                      '&##################@!         
                  %################@@#######|           `;:.         `$##############@@%`          
                 .|##@#####@#%.   `:|$@#####|    '|&####@&#$        .|@############@@&'            
                     :&###@@|.        .%####|    |##########&'   `%##@###########@@&:              
                        `|@|          .%####|    |############@@#################&:                
                                      .$#@@#|    |###########################@#%`                  
                                       :|%$&$$&&&###########################$'                     
                                            :@#@######################@@#$'                        
                                            :@###################@###$;.                           
                                            :@############@@####@|'                                
                                            ;@#@@########@%;'.                                     
"""


class prayer:
    def __init__(self, halt_speed: float=0.005,):
        self.holy_img = holy_img
        # Width of the icon, used to center all text so it aligns with the skull
        lines = self.holy_img.splitlines()
        self.scroll_width = max(len(line) for line in lines) if lines else 60
        
        # Locate the JSON file inside the installed package
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_path, 'holy_words.json')

        with open(json_path, 'r', encoding='utf-8') as filo:
            self.holy_words = json.load(filo)['holy_words']
        
        self.halt_speed = halt_speed
        # ANSI color codes for extra holy vibes
        self.red = "\033[91m"
        self.cyan = "\033[96m"
        self.yellow = "\033[93m"
        self.reset = "\033[0m"
        self.bold = "\033[1m"
        # Machine Cant glyphs and scroll structure, inspired by purity seals
        self.glyphs = ["†", "✚", "⚙", "☉", "⇋", "Σ"]
        self.scroll_header = [
            "Praise the Omnissiah!",
            "Glory to the Omnissiah!",
        ]
        self.scroll_footer = [
            "Our enemies may rest, but rust never sleeps.",
            "Adeptus Mechanicus — The Priesthood of Mars.",
        ]
        self.chants = [
            "+++ BLESS THE CIRCUITS +++",
            ">>> PURGE THE IMPURE CODE <<<",
            "01110010 01100101 01110110 01100101 01110010 01100101",
            "⚙ SYSTEM SANCTIFIED ⚙",
        ]

    def _log(self, message: str, fast: bool = False):
        # Optionally speed up output (used for binary mode)
        delay_base = self.halt_speed / 5 if fast else self.halt_speed
        for element in message:
            print(element, end='', flush=True)
            # Slightly randomize the delay for a more "alive" machine-spirit effect
            time.sleep(delay_base + random.uniform(0, delay_base))
        
        print('\n')

    def _print_border(self):
        border = "".join(random.choice(self.glyphs) for _ in range(self.scroll_width))
        print(f"{self.red}{self.bold}{border}{self.reset}")

    def _to_binary(self, text: str, group: int = 11) -> str:
        # Convert each character to its 8-bit ASCII binary form, wrapped to avoid overlong lines
        bits = [f"{ord(c):08b}" for c in text]
        lines = []
        for i in range(0, len(bits), group):
            lines.append(' '.join(bits[i:i+group]))
        return '\n'.join(lines)

    def pray(self):
        # Clear screen for a dramatic entrance
        # print("\033[2J\033[H", end='')
        # Cog-skull sigil in red, like a purity seal rosette
        print(f"{self.red}{self.bold}{self.holy_img}{self.reset}")

        # Scroll-like litany header
        self._print_border()
        for line in self.scroll_header:
            centered = line.center(self.scroll_width)
            self._log(f"{self.bold}{self.yellow}{centered}{self.reset}")
        self._print_border()

        # Small glyph row, like techno-heraldry
        glyph_row = " ".join(random.choice(self.glyphs) for _ in range(7))
        glyph_row_centered = glyph_row.center(self.scroll_width)
        self._log(f"{self.red}{glyph_row_centered}{self.reset}")

        seed(time.time())
        prayer = choice(self.holy_words)

        # 50% chance to activate binary translation
        binary_mode = (random.random() < 0.5)
        # binary_mode = True

        for index, holy_content in enumerate(prayer):
            if binary_mode:
                # Convert the raw sentence to binary and wrap it into shorter lines
                content = self._to_binary(holy_content)
                # In binary mode, print much faster
                self._log(f"{content}", fast=True)
            else:
                content = holy_content.center(self.scroll_width)
                self._log(f"{content}")

            # Insert a canticle halfway through the prayer
            if index == len(prayer) // 2 and self.chants:
                chant = random.choice(self.chants)
                if binary_mode:
                    chant_content = self._to_binary(chant)
                else:
                    chant_content = chant.center(self.scroll_width)
                self._log(f"{self.red}{self.bold}{chant_content}{self.reset}", fast=binary_mode)

        # Footer like the bottom of the scroll
        self._print_border()
        for line in self.scroll_footer:
            centered = line.center(self.scroll_width)
            self._log(f"{self.bold}{self.yellow}{centered}{self.reset}")
        self._print_border()

        final_line = "[*] PRAISE THE GOD OF ALL MACHINES - THE MIGHTY OMNISSIAH!!!"
        centered_final = final_line.center(self.scroll_width)
        self._log(f"\n{self.bold}{self.yellow}{centered_final}{self.reset}\n")


if __name__ == "__main__":
    # We shall praise the great Omnissiah!
    prayer = prayer()
    prayer.pray()
