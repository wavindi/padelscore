import tkinter as tk
from datetime import datetime
import math

class PadelScoreboardProfessional:
    def __init__(self, root):
        self.root = root
        self.root.title("Padel Scoreboard Professional")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)

        # Game variables
        self.match_started = False
        self.start_time = None
        self.current_set = 1
        self.match_number = 1
        
        # Tennis scoring
        self.team1_game_points = 0  # Current game points
        self.team2_game_points = 0
        self.team1_games = 0        # Games won
        self.team2_games = 0
        self.team1_sets = 0         # Sets won
        self.team2_sets = 0

        # Team names - CHANGED TO WAJDI AND MALEK
        self.team1_name = "WAJDI TEAM"
        self.team2_name = "MALEK TEAM"

        # Colors matching the image
        self.red_color = '#e74c3c'      # Team 1 (left) - Red
        self.blue_color = '#2c3e50'     # Team 2 (right) - Dark Blue
        self.black_bg = '#000000'       # Background
        self.white_text = '#ffffff'     # White text
        self.digital_green = '#00ff00'  # Digital display green

        # Get screen dimensions
        self.root.update_idletasks()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.create_interface()
        self.update_timer()

    def create_interface(self):
        # Main canvas for custom drawing
        self.canvas = tk.Canvas(self.root, bg=self.black_bg, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Bind canvas click events for touch
        self.canvas.bind('<Button-1>', self.handle_touch)
        
        self.draw_interface()

    def draw_interface(self):
        """Draw the complete interface matching the image"""
        self.canvas.delete("all")  # Clear canvas
        
        w = self.screen_width
        h = self.screen_height
        
        # 1. TOP HEADER BAR
        header_height = h * 0.15
        self.canvas.create_rectangle(0, 0, w, header_height, fill=self.black_bg, outline="")
        
        # Logo and title (left)
        self.canvas.create_text(w*0.05, header_height*0.3, text="🏓 PadelScore", 
                               font=('Arial', int(header_height*0.25), 'bold'), 
                               fill=self.white_text, anchor='w')
        
        # Timer (center top)
        timer_text = "TAP TO START" if not self.match_started else self.get_timer_text()
        self.canvas.create_text(w*0.5, header_height*0.2, text=timer_text, 
                               font=('Arial', int(header_height*0.2), 'bold'), 
                               fill='red', anchor='center')
        
        # Match info (right)
        self.canvas.create_text(w*0.95, header_height*0.25, text=f"MATCH {self.match_number} / 3", 
                               font=('Arial', int(header_height*0.15), 'bold'), 
                               fill=self.white_text, anchor='e')

        # 2. DIAGONAL SPLIT DESIGN
        main_area_y = header_height
        main_area_height = h - header_height
        
        # Calculate diagonal line points
        diagonal_start_x = w * 0.35
        diagonal_end_x = w * 0.65
        
        # Left side (RED) - Team 1 (WAJDI TEAM)
        points_left = [0, main_area_y, diagonal_start_x, main_area_y, 
                      diagonal_end_x, h, 0, h]
        self.canvas.create_polygon(points_left, fill=self.red_color, outline="")
        
        # Right side (BLUE) - Team 2 (MALEK TEAM)
        points_right = [diagonal_start_x, main_area_y, w, main_area_y,
                       w, h, diagonal_end_x, h]
        self.canvas.create_polygon(points_right, fill=self.blue_color, outline="")
        
        # 3. CENTER DIAGONAL STRIP
        strip_width = w * 0.08
        strip_start = w*0.5 - strip_width/2
        strip_end = w*0.5 + strip_width/2
        
        # Diagonal strip background
        strip_points = [strip_start, main_area_y, strip_end, main_area_y,
                       strip_end + strip_width*0.5, h, strip_start + strip_width*0.5, h]
        self.canvas.create_polygon(strip_points, fill='#34495e', outline="")
        
        # "VS" text in center
        self.canvas.create_text(w*0.5, main_area_y + main_area_height*0.3, text="VS", 
                               font=('Arial', int(h*0.08), 'bold'), 
                               fill=self.white_text, anchor='center')
        
        # Team indicators
        self.canvas.create_text(w*0.5, main_area_y + main_area_height*0.7, text="Team", 
                               font=('Arial', int(h*0.03)), 
                               fill='red', anchor='center')
        self.canvas.create_text(w*0.5, main_area_y + main_area_height*0.8, text="02", 
                               font=('Arial', int(h*0.05), 'bold'), 
                               fill='red', anchor='center')

        # 4. TEAM 1 (LEFT/RED) CONTENT - WAJDI TEAM
        team1_center_x = w * 0.2
        team1_center_y = main_area_y + main_area_height * 0.5
        
        # WAJDI TEAM name
        self.canvas.create_text(team1_center_x, main_area_y + main_area_height*0.15, 
                               text=self.team1_name, 
                               font=('Arial', int(h*0.05), 'bold'), 
                               fill=self.white_text, anchor='center')
        
        # Team 1 current game score (large)
        game_score_1 = self.get_display_score(self.team1_game_points, self.team2_game_points, 1)
        self.canvas.create_text(team1_center_x, team1_center_y, text=game_score_1, 
                               font=('Arial', int(h*0.25), 'bold'), 
                               fill=self.white_text, anchor='center')
        
        # Team 1 games/sets (bottom)
        self.canvas.create_text(team1_center_x*0.3, main_area_y + main_area_height*0.85, 
                               text=str(self.team1_sets), 
                               font=('Arial', int(h*0.06), 'bold'), 
                               fill=self.white_text, anchor='center')
        self.canvas.create_text(team1_center_x*0.6, main_area_y + main_area_height*0.85, 
                               text=str(self.team1_games), 
                               font=('Arial', int(h*0.06), 'bold'), 
                               fill=self.white_text, anchor='center')
        self.canvas.create_text(team1_center_x*0.9, main_area_y + main_area_height*0.85, 
                               text="- -", 
                               font=('Arial', int(h*0.06), 'bold'), 
                               fill=self.white_text, anchor='center')

        # 5. TEAM 2 (RIGHT/BLUE) CONTENT - MALEK TEAM
        team2_center_x = w * 0.8
        team2_center_y = main_area_y + main_area_height * 0.5
        
        # MALEK TEAM name
        self.canvas.create_text(team2_center_x, main_area_y + main_area_height*0.15, 
                               text=self.team2_name, 
                               font=('Arial', int(h*0.05), 'bold'), 
                               fill=self.white_text, anchor='center')
        
        # Team 2 current game score (large)
        game_score_2 = self.get_display_score(self.team1_game_points, self.team2_game_points, 2)
        self.canvas.create_text(team2_center_x, team2_center_y, text=game_score_2, 
                               font=('Arial', int(h*0.25), 'bold'), 
                               fill=self.white_text, anchor='center')
        
        # Team 2 games/sets (bottom)
        self.canvas.create_text(team2_center_x*1.25, main_area_y + main_area_height*0.85, 
                               text=str(self.team2_sets), 
                               font=('Arial', int(h*0.06), 'bold'), 
                               fill=self.white_text, anchor='center')
        self.canvas.create_text(team2_center_x*1.15, main_area_y + main_area_height*0.85, 
                               text=str(self.team2_games), 
                               font=('Arial', int(h*0.06), 'bold'), 
                               fill=self.white_text, anchor='center')
        self.canvas.create_text(team2_center_x*1.05, main_area_y + main_area_height*0.85, 
                               text="- -", 
                               font=('Arial', int(h*0.06), 'bold'), 
                               fill=self.white_text, anchor='center')

        # 6. RESET BUTTON (small, top right)
        reset_x = w * 0.95
        reset_y = header_height * 0.7
        reset_button_rect = self.canvas.create_rectangle(reset_x-40, reset_y-15, reset_x+40, reset_y+15, 
                                                       fill='#e67e22', outline="", tags="reset_button")
        reset_button_text = self.canvas.create_text(reset_x, reset_y, text="RESET", 
                                                  font=('Arial', 12, 'bold'), 
                                                  fill=self.white_text, anchor='center', tags="reset_button")
        
        # Bind reset button click
        self.canvas.tag_bind("reset_button", "<Button-1>", self.reset_match)

    def handle_touch(self, event):
        """Handle touch events"""
        # Check if reset button was clicked first
        if self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1):
            overlapping = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
            for item in overlapping:
                if "reset_button" in self.canvas.gettags(item):
                    return  # Reset button handles its own click
        
        if not self.match_started:
            self.start_match()
            return
        
        # Determine which side was touched
        if event.x < self.screen_width / 2:
            self.team1_scores()
            print("WAJDI TEAM scores!")
        else:
            self.team2_scores()
            print("MALEK TEAM scores!")

    def get_display_score(self, team1_points, team2_points, team):
        """Get display score for tennis scoring"""
        point_map = {0: "0", 1: "15", 2: "30", 3: "40"}
        
        if team1_points >= 3 and team2_points >= 3:
            if team1_points == team2_points:
                return "40"  # Deuce shows as 40-40
            elif team == 1:
                return "AD" if team1_points > team2_points else "40"
            else:
                return "AD" if team2_points > team1_points else "40"
        else:
            if team == 1:
                return point_map.get(team1_points, str(team1_points))
            else:
                return point_map.get(team2_points, str(team2_points))

    def team1_scores(self):
        """WAJDI TEAM scores a point"""
        self.team1_game_points += 1
        self.check_game_winner()
        self.draw_interface()

    def team2_scores(self):
        """MALEK TEAM scores a point"""
        self.team2_game_points += 1
        self.check_game_winner()
        self.draw_interface()

    def check_game_winner(self):
        """Check for game winner"""
        if self.team1_game_points >= 3 and self.team2_game_points >= 3:
            if abs(self.team1_game_points - self.team2_game_points) >= 2:
                if self.team1_game_points > self.team2_game_points:
                    self.team1_games += 1
                    print("WAJDI TEAM wins game!")
                else:
                    self.team2_games += 1
                    print("MALEK TEAM wins game!")
                self.reset_game()
        elif self.team1_game_points >= 4 and self.team2_game_points < 3:
            self.team1_games += 1
            print("WAJDI TEAM wins game!")
            self.reset_game()
        elif self.team2_game_points >= 4 and self.team1_game_points < 3:
            self.team2_games += 1
            print("MALEK TEAM wins game!")
            self.reset_game()

    def reset_game(self):
        """Reset current game points"""
        self.team1_game_points = 0
        self.team2_game_points = 0

    def start_match(self):
        """Start match"""
        self.match_started = True
        self.start_time = datetime.now()
        self.draw_interface()
        print("Match started between WAJDI TEAM vs MALEK TEAM!")

    def reset_match(self, event=None):
        """Reset entire match"""
        self.team1_game_points = 0
        self.team2_game_points = 0
        self.team1_games = 0
        self.team2_games = 0
        self.team1_sets = 0
        self.team2_sets = 0
        self.match_started = False
        self.start_time = None
        self.draw_interface()
        print("Match reset! WAJDI TEAM vs MALEK TEAM ready to start.")

    def get_timer_text(self):
        """Get formatted timer text"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return f"{mins:02d}:{secs:02d}"
        return "00:00"

    def update_timer(self):
        """Update timer display"""
        if self.match_started:
            self.draw_interface()
        self.root.after(5000, self.update_timer)  # Update every 5 seconds

def main():
    root = tk.Tk()
    app = PadelScoreboardProfessional(root)
    root.bind('<Escape>', lambda e: root.quit())
    root.mainloop()

if __name__ == "__main__":
    main()
