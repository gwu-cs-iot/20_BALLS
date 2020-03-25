import cv2

FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.5
FONT_THICKNESS = 1

(_, label_height), baseline = cv2.getTextSize('E', FONT_FACE, FONT_SIZE, FONT_THICKNESS)

def drawHud(frame, ballcircles):
    line_y = label_height

    cv2.putText(frame, 'Ball states', (0, line_y), cv2.FONT_HERSHEY_SIMPLEX, FONT_SIZE, (255, 0, 0), thickness=FONT_THICKNESS)

    for bc in ballcircles:
        line_y += label_height
        cv2.putText(frame, f'{bc.ball.name}: {bc.state.name}', (0, line_y), FONT_FACE, FONT_SIZE, (255, 0, 0), thickness=FONT_THICKNESS)