        if pipe.get('type') == 'bottom' and pipe['rect'].centerx < bird_rect.centerx and not pipe['scored']:
                score += 1
                pipe['scored'] = True
                score_sound.play()