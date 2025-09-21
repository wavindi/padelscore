import tkinter as tk
from datetime import datetime

class PadelTouchscreen7inch:
    def __init__(self, root):
        self.root = root
        self.root.title("Padel Scoreboard - 7inch Touch")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)

        # Game variables
        self.match_started = False
        self.start_time = None
        
        self.green_game_points = 0
        self.red_game_points = 0
        self.green_games = 0
        self.red_games = 0

        # Get actual screen dimensions
        self.root.update_idletasks()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        print(f"Screen: {self.screen_width} x {self.screen_height}")

        # Create interface optimized for 7-inch
        self.create_interface()
        self.update_timer()

    def create_interface(self):
        # Calculate dimensions for 7-inch screen
        banner_height = int(self.screen_height * 0.25)  # 25% for banner
        button_area_height = self.screen_height - banner_height
        button_width = self.screen_width // 2  # Exactly half each

        print(f"Banner height: {banner_height}, Button area: {button_area_height}")
        print(f"Button width: {button_width}")

        # 1. BANNER (25% of screen height)
        self.banner = tk.Frame(self.root, bg='#34495e', height=banner_height)
        self.banner.place(x=0, y=0, width=self.screen_width, height=banner_height)
        
        # Banner layout - 3 equal columns
        col_width = self.screen_width // 3
        
        # Left column - Timer
        timer_frame = tk.Frame(self.banner, bg='#34495e')
        timer_frame.place(x=0, y=0, width=col_width, height=banner_height)
        
        tk.Label(timer_frame, text="TIME", 
                font=('Arial', 14, 'bold'), bg='#34495e', fg='#bdc3c7').pack(pady=(15, 2))
        
        self.timer_label = tk.Label(timer_frame, text="TAP TO START", 
                                   font=('Arial', 18, 'bold'), 
                                   bg='#34495e', fg='white')
        self.timer_label.pack()

        # Center column - Global scores
        score_frame = tk.Frame(self.banner, bg='#34495e')
        score_frame.place(x=col_width, y=0, width=col_width, height=banner_height)
        
        tk.Label(score_frame, text="GAMES WON", 
                font=('Arial', 16, 'bold'), bg='#34495e', fg='#f39c12').pack(pady=(10, 5))
        
        # Score container
        score_container = tk.Frame(score_frame, bg='#34495e')
        score_container.pack(expand=True)
        
        self.green_games_label = tk.Label(score_container, text="0", 
                                         font=('Arial', 32, 'bold'), 
                                         bg='#34495e', fg='#27ae60')
        self.green_games_label.pack(side='left', padx=15)
        
        tk.Label(score_container, text="-", 
                font=('Arial', 32, 'bold'), 
                bg='#34495e', fg='white').pack(side='left', padx=8)
        
        self.red_games_label = tk.Label(score_container, text="0", 
                                       font=('Arial', 32, 'bold'), 
                                       bg='#34495e', fg='#e74c3c')
        self.red_games_label.pack(side='left', padx=15)

        # Right column - Reset button
        reset_frame = tk.Frame(self.banner, bg='#34495e')
        reset_frame.place(x=col_width * 2, y=0, width=col_width, height=banner_height)
        
        self.reset_button = tk.Button(reset_frame, text="RESET", 
                                     font=('Arial', 16, 'bold'),
                                     bg='#e67e22', fg='white',
                                     activebackground='#d35400',
                                     relief='flat', bd=0,
                                     command=self.reset_match)
        self.reset_button.place(relx=0.5, rely=0.5, anchor='center', 
                               width=80, height=40)

        # 2. LEFT BUTTON (GREEN) - EXACT POSITIONING
        self.green_button = tk.Button(
            self.root,
            text="GREEN TEAM\n\n0",
            font=('Arial', 42, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#2ecc71',
            relief='flat',
            bd=0,
            command=self.green_scores
        )
        self.green_button.place(x=0, y=banner_height, 
                               width=button_width, height=button_area_height)

        # 3. RIGHT BUTTON (RED) - EXACT POSITIONING  
        self.red_button = tk.Button(
            self.root,
            text="RED TEAM\n\n0",
            font=('Arial', 42, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#ff5733',
            relief='flat',
            bd=0,
            command=self.red_scores
        )
        self.red_button.place(x=button_width, y=banner_height, 
                             width=button_width, height=button_area_height)

    def points_to_display(self, points):
        """Convert tennis points to display"""
        point_map = {0: "0", 1: "15", 2: "30", 3: "40"}
        return point_map.get(points, str(points))

    def green_scores(self):
        """Green team scores"""
        if not self.match_started:
            self.start_match()
            return
            
        self.green_game_points += 1
        self.check_game_winner()
        self.update_display()

    def red_scores(self):
        """Red team scores"""
        if not self.match_started:
            self.start_match()
            return
            
        self.red_game_points += 1
        self.check_game_winner()
        self.update_display()

    def check_game_winner(self):
        """Tennis scoring rules"""
        green_points = self.green_game_points
        red_points = self.red_game_points
        
        if green_points >= 3 and red_points >= 3:
            if abs(green_points - red_points) >= 2:
                if green_points > red_points:
                    self.green_wins_game()
                else:
                    self.red_wins_game()
        elif green_points >= 4 and red_points < 3:
            self.green_wins_game()
        elif red_points >= 4 and green_points < 3:
            self.red_wins_game()

    def green_wins_game(self):
        """Green wins game"""
        self.green_games += 1
        self.reset_current_game()

    def red_wins_game(self):
        """Red wins game"""
        self.red_games += 1
        self.reset_current_game()

    def reset_current_game(self):
        """Reset current game points"""
        self.green_game_points = 0
        self.red_game_points = 0

    def update_display(self):
        """Update all displays"""
        # Handle deuce/advantage
        if self.green_game_points >= 3 and self.red_game_points >= 3:
            if self.green_game_points == self.red_game_points:
                green_display = "DEUCE"
                red_display = "DEUCE"
            elif self.green_game_points > self.red_game_points:
                green_display = "ADV"
                red_display = "40"
            else:
                green_display = "40"
                red_display = "ADV"
        else:
            green_display = self.points_to_display(self.green_game_points)
            red_display = self.points_to_display(self.red_game_points)

        # Update buttons
        self.green_button.config(text=f"GREEN TEAM\n\n{green_display}")
        self.red_button.config(text=f"RED TEAM\n\n{red_display}")
        
        # Update global scores
        self.green_games_label.config(text=str(self.green_games))
        self.red_games_label.config(text=str(self.red_games))

    def start_match(self):
        """Start match"""
        self.match_started = True
        self.start_time = datetime.now()
        self.timer_label.config(text="00:00")

    def reset_match(self):
        """Reset everything"""
        self.green_game_points = 0
        self.red_game_points = 0
        self.green_games = 0
        self.red_games = 0
        self.match_started = False
        self.timer_label.config(text="TAP TO START")
        self.start_time = None
        self.update_display()

    def update_timer(self):
        """Update timer"""
        if self.match_started and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        
        self.root.after(1000, self.update_timer)

def main():
    root = tk.Tk()
    app = PadelTouchscreen7inch(root)
    root.bind('<Escape>', lambda e: root.quit())
    root.mainloop()

if __name__ == "__main__":
    main()
