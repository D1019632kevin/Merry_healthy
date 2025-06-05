from PyQt5.QtCore import QTimer

class show_score:
    def __init__(self, parent,ui):
        self.ui = ui
        self.set = parent
    def show_score(self):
        self.ui.label_10.setText(f"Score: {float(self.set.total_score):.2f}")
        if self.ui.stackedWidget.currentIndex() == 3:
            self.ui.label_34.setText(f"Score: {float(self.set.total_score):.2f}")

    def score_cal(self, dif_time):
        if self.set.stop_score_and_combo:
            return
        best = self.set.beat_interval * 0.2
        nice = self.set.beat_interval * 0.4
        not_bad = self.set.beat_interval * 0.8
    
        if self.set.combo < 5:  #計算combo倍率
            self.set.combo_mult = 1.0
        elif self.set.combo < 9:
            self.set.combo_mult = 1.1
        elif self.set.combo < 13:
            self.set.combo_mult = 1.2
        else:
            self.set.combo_mult = 1.3

        score_add = 0

        if abs(dif_time) < best:
            score_add = 3 * self.set.combo_mult
            self.combo += 1
        elif abs(dif_time) <= nice:
            score_add = 2 * self.set.combo_mult
            self.combo += 1
        elif abs(dif_time) <= not_bad:
            score_add = 1
            self.set.combo = 0
        else:
            score_add = 0
            self.set.combo = 0
       
        self.set.total_score += score_add  

        if score_add > 0:
            self.set.last_score_add = f"+{score_add:.2f}"
            self.set.show_score_add = True

        QTimer.singleShot(0, self.set.update_fire_effect)