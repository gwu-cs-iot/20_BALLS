import cv2

FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_FACE_HEADER = cv2.FONT_HERSHEY_DUPLEX
FONT_SIZE = 0.4
FONT_THICKNESS = 1

(_, LABEL_HEIGHT_HEADER), _ = cv2.getTextSize('TEST', FONT_FACE_HEADER, FONT_SIZE, FONT_THICKNESS)
(_, LABEL_HEIGHT), _ = cv2.getTextSize('TEST', FONT_FACE, FONT_SIZE, FONT_THICKNESS)

LINE_SPACING = 20


def drawHud(frame, ballcircles):
    line_y = LABEL_HEIGHT_HEADER

    cv2.putText(frame, 'Ball states', (0, line_y), FONT_FACE_HEADER, FONT_SIZE, (255, 0, 0), thickness=FONT_THICKNESS)

    for bc in ballcircles:
        if bc.circle is not None:
            line_y += LABEL_HEIGHT + LINE_SPACING
            cv2.putText(frame, f'{bc.name}: {bc.state.name} {bc.throwstate.name} pos:{str(bc.circle.coords)} jump:{str(bc.jumpPoint)}',
                        (0, line_y), FONT_FACE, FONT_SIZE, (255, 0, 0), thickness=FONT_THICKNESS)

            cv2.putText(frame, f'xvel:{str(bc.movement.xvel)} yvel:{str(bc.movement.yvel)}', (0,line_y+13), FONT_FACE, FONT_SIZE, (255,0,0), thickness=FONT_THICKNESS)
