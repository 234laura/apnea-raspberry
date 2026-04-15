:- dynamic frecuencia_cardiaca/1.
:- dynamic spo2/1.
:- dynamic movimiento/1.
:- dynamic pausa_respiratoria_seg/1.

clasificacion(grave) :-
    pausa_respiratoria_seg(P), P >= 20,
    spo2(S), S < 90, !.

clasificacion(grave) :-
    spo2(S), S < 88, !.

clasificacion(moderada) :-
    pausa_respiratoria_seg(P), P >= 10, P < 20,
    spo2(S), S < 94, !.

clasificacion(moderada) :-
    frecuencia_cardiaca(F), (F < 50 ; F > 110),
    movimiento(M), M < 0.05, !.

clasificacion(normal).