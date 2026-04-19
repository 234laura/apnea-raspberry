% ============================================================
%  apnea_rules.pl  –  Motor de inferencia de apnea del sueño
%  Variables dinámicas inyectadas desde Python en cada ciclo
% ============================================================

:- dynamic frecuencia_cardiaca/1.
:- dynamic spo2/1.
:- dynamic movimiento/1.
:- dynamic pausa_respiratoria_seg/1.
:- dynamic tendencia_spo2/1.      % pendiente media de SpO2 (% por muestra)

% ------------------------------------------------------------
%  GRAVE – máxima prioridad
% ------------------------------------------------------------

% Apnea clásica: pausa larga + hipoxemia severa
clasificacion(grave) :-
    pausa_respiratoria_seg(P), P >= 20,
    spo2(S), S < 90, !.

% Hipoxemia severa sin importar la pausa
clasificacion(grave) :-
    spo2(S), S < 88, !.

% Caída rápida de SpO2 (tendencia negativa fuerte) + hipoxemia
clasificacion(grave) :-
    tendencia_spo2(T), T < -1.5,
    spo2(S), S < 93, !.

% Bradicardia extrema + hipoxemia moderada
clasificacion(grave) :-
    frecuencia_cardiaca(F), F < 40,
    spo2(S), S < 92, !.

% ------------------------------------------------------------
%  MODERADA
% ------------------------------------------------------------

% Pausa media + desaturación moderada
clasificacion(moderada) :-
    pausa_respiratoria_seg(P), P >= 10, P < 20,
    spo2(S), S < 94, !.

% FC fuera de rango normal + paciente quieto (posible evento vagal)
clasificacion(moderada) :-
    frecuencia_cardiaca(F), (F < 50 ; F > 110),
    movimiento(M), M < 0.08, !.

% Taquicardia + desaturación moderada
clasificacion(moderada) :-
    frecuencia_cardiaca(F), F > 120,
    spo2(S), S < 95, !.

% Desaturación moderada sin pausa larga (hipoxemia leve sostenida)
clasificacion(moderada) :-
    spo2(S), S >= 88, S < 92, !.

% Caída progresiva de SpO2 (tendencia negativa) aunque aún en rango
clasificacion(moderada) :-
    tendencia_spo2(T), T < -0.8,
    spo2(S), S < 95, !.

% ------------------------------------------------------------
%  SIN DATOS – sensor no válido o dedo ausente
% ------------------------------------------------------------
clasificacion(sin_datos) :-
    \+ spo2(_), !.

% ------------------------------------------------------------
%  NORMAL – fallback cuando no se cumple ninguna regla anterior
% ------------------------------------------------------------
clasificacion(normal).