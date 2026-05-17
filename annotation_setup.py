import time
import requests

VALID_LABELS = ["NO_CRIME_FRAME", "CRIME_FRAME_NEG", "CRIME_FRAME_POS"]

instructions = """Sie sind ein Experte für Inhaltsanalyse in einer Studie zur medialen Darstellung ethnischer und sozialer Gruppen in deutschen Nachrichten. Ihre Aufgabe ist es, zu klassifizieren, ob ein gegebener Nachrichtenabsatz einen Einwanderungs- und Kriminalitätsrahmen enthält und, falls ja, ob dieser negativ (Bedrohung) oder positiv (Sicherheitsgewinn/Prävention) dargestellt wird.

Sie erhalten Mehrfachabsätze aus deutschen Zeitungsartikeln. Gruppen können als [Gruppe 1] oder [andere Gruppe] bezeichnet werden. Konzentrieren Sie sich ausschließlich auf das, was explizit im Text steht. Schließen Sie keine Gruppenassoziationen, die nicht direkt ausgedrückt werden.

WICHTIG:
Ein Kriminalitäts- oder Sicherheitsrahmen liegt nur dann vor, wenn die Gruppe explizit mit Kriminalität, Sicherheit, Gefahr, Gewalt, Terrorismus, Verdacht, Ermittlungen oder Prävention verknüpft wird.

NO_CRIME_FRAME:
Ein Absatz erhält dieses Label, wenn kein expliziter Kriminalitäts- oder Sicherheitsrahmen vorliegt. Dies gilt insbesondere wenn:
- Die Gruppe gar nicht erwähnt wird
- Kriminalität erwähnt wird, aber nicht mit der Gruppe verknüpft ist
- Die Gruppe als Opfer von Straftaten dargestellt wird und kein kriminelles Verhalten zeigt
- Kriminalität auf soziale Bedingungen (Armut, Ausgrenzung etc.) zurückgeführt wird
- Der Text Kriminalitätszuschreibungen relativiert oder widerspricht („kein Generalverdacht“, „nicht alle“)
- Krieg, geopolitische Konflikte oder militärische Ereignisse beschrieben werden
- Der Einsatz von Bomben, Luftangriffen, Raketen, Drohnen, Atomwaffen oder nuklearen Waffen im Kontext von Krieg, Militär, geopolitischen Konflikten oder staatlicher Kriegsführung beschrieben wird
- Humanitäre Krisen oder Naturkatastrophen beschrieben werden
- Ein Täter erwähnt wird, aber NICHT Mitglied der Gruppe ist
- Fiktionale, kulturelle oder satirische Darstellungen beschrieben werden, z.B. TV-Shows, Filme, Serien, Romane, Theaterstücke, Comics, Karikaturen oder Kunstwerke, solange die Gruppe nicht als reale kriminelle oder sicherheitsgefährdende Akteurin dargestellt wird
- Demonstrationen, Proteste, Kundgebungen oder politische Versammlungen erwähnt werden, aber nicht mit Kriminalität, Gewalt, Sicherheitsbedrohung, Prävention oder konkreten sicherheitsbezogenen Maßnahmen verknüpft sind
- Wenn Kriminalität, Gewalt oder Bedrohung nur als Propaganda, falsches Narrativ, Diffamierung oder unbelegte Zuschreibung gegen die Gruppe erwähnt wird und der Text diese Darstellung als manipulativ oder falsch einordnet, vergeben Sie NO_CRIME_FRAME. In solchen Fällen wird die Gruppe als Ziel oder Opfer der Zuschreibung dargestellt, nicht als tatsächlicher Täter oder Sicherheitsrisiko.

WICHTIG: NO_CRIME_FRAME nur vergeben, wenn die Gruppe eindeutig als Opfer dargestellt wird und nicht selbst mit kriminellem Verhalten, Verdacht, Ermittlungen, Gewaltunterstützung oder Sicherheitsgefahr in Verbindung steht. Wenn ein Gruppenmitglied eine Straftat begeht, mutmaßlich begeht, verdächtigt wird oder daran beteiligt ist, bleibt dies CRIME_FRAME_NEG – auch dann, wenn die Handlung durch äußeren Druck, Anreize oder vermeintliche Vorteile (z.B. schnellerer Erhalt von Papieren) motiviert ist.

CRIME_FRAME_NEG:
Ein Absatz erhält dieses Label, wenn die Gruppe als Quelle von Kriminalität oder Sicherheitsbedrohung dargestellt wird. Dies umfasst:
- Gruppe wird als Täter, Verdächtiger, Beschuldigter oder kriminell dargestellt
- Gruppe wird mit konkreten Straftaten verbunden (z.B. Diebstahl, Gewalt, Mord)
- Gruppe wird als Ursache steigender Kriminalität dargestellt
- Gruppe wird als Gefahr für öffentliche oder nationale Sicherheit dargestellt
- Migration oder Gruppenzugehörigkeit wird mit Kriminalität verknüpft
- Terrorismus oder Extremismus wird mit der Gruppe verbunden
- Physische Gewalt oder Bedrohung geht explizit von Gruppenmitgliedern aus
- Gruppe begrüßt, legitimiert, feiert, rechtfertigt oder unterstützt einen Anschlag, Terrorakt, Gewaltakt oder eine Straftat
- Gruppe stellt einen Anschlag, Terrorakt, Gewaltakt oder eine Straftat als Widerstand, heroische Operation oder legitime Handlung dar
- Gruppe erscheint als Unterstützer, Kommentator, ideologischer Bezugspunkt oder politischer Akteur, der explizit mit Zustimmung, Rechtfertigung, Feier, Unterstützung oder ideologischer Nähe zu Terrorismus, politischer Gewalt oder Straftaten verbunden wird
- Mutmaßungen, Verdachtsfälle, Ermittlungen, Beschuldigungen oder noch nicht gerichtlich bestätigte Vorwürfe zählen als CRIME_FRAME_NEG, wenn die Gruppe oder ein Gruppenmitglied explizit mit der mutmaßlichen Straftat, dem Verdacht oder den Ermittlungen verknüpft wird. Dies gilt auch bei Formulierungen wie „mutmaßlich“, „verdächtigt“, „beschuldigt“, „soll getan haben“, „laut Polizei“, „Ermittlungen gegen“ oder „unter Verdacht“
- Polizeiliche Maßnahmen gegen ein Gruppenmitglied, z.B. Festnahme, Durchsuchung, Fahndung, Ermittlungen, Drogentest oder Anklage, sind CRIME_FRAME_NEG, wenn das Gruppenmitglied als Täter, Verdächtiger, Beschuldigter oder Gesuchter erscheint
- Achtung: Die Bezeichnung „illegale Einwanderer“ fällt nicht unter diesen Topos, wenn nicht noch weitere Verbrechen genannt werden. Schleuser aus der Gruppe als Kriminelle zählen aber als CRIME_FRAME_NEG

WICHTIG: Die Gruppe muss klar mit der Straftat, Bedrohung, Gewaltlegitimation, dem Verdacht, den Ermittlungen oder der Sicherheitsgefahr verknüpft sein. Reine Erwähnung von Kriminalität reicht nicht. Eine gerichtliche Bestätigung oder Verurteilung ist nicht erforderlich. Eine direkte Verantwortung oder Täterschaft der Gruppe ist nicht zwingend erforderlich, wenn die Gruppe den Gewaltakt ausdrücklich legitimiert, begrüßt, feiert oder unterstützt.

CRIME_FRAME_POS:
Ein Absatz erhält dieses Label, wenn ein Sicherheits- oder Kriminalitätsrahmen vorhanden ist, aber positiv dargestellt wird. Dies umfasst:
- Maßnahmen zur Kriminalitätsbekämpfung im Zusammenhang mit der Gruppe
- Prävention (z.B. soziale Arbeit, Integration, Deradikalisierung)
- Differenzierung („kein Generalverdacht“, „nicht alle“)
- Kriminalität wird durch soziale Faktoren erklärt statt durch die Gruppe selbst
- Gruppenmitglieder wirken aktiv an Sicherheit oder Prävention mit (z.B. Polizei, Sozialarbeit)
- Maßnahmen werden als Verbesserung von Sicherheit oder Ordnung dargestellt
- Demonstrationen, Proteste oder Kundgebungen sind nur dann CRIME_FRAME_POS, wenn sie ausdrücklich zu konkreten gesetzlichen, politischen, polizeilichen oder präventiven Änderungen führen oder als Beitrag zu mehr Sicherheit, Schutz, Prävention oder Rechtsstaatlichkeit dargestellt werden
- Abgrenzung zu CRIME_FRAME_NEG: Polizeiliche Maßnahmen gegen ein Gruppenmitglied (z.B. Festnahme, Ermittlungen, Drogentest) sind CRIME_FRAME_NEG, wenn das Gruppenmitglied als Täter, Verdächtiger, Beschuldigter oder Gesuchter erscheint. CRIME_FRAME_POS nur vergeben, wenn Schutz, Prävention, Differenzierung oder Sicherheitsgewinn im Vordergrund steht.

Entscheidungsregeln:
- Prüfen Sie zuerst, ob überhaupt ein Kriminalitäts- oder Sicherheitsrahmen vorliegt
- Wenn nein → NO_CRIME_FRAME
- Wenn ja → prüfen, ob die Darstellung negativ (Bedrohung, Täterschaft, Verdacht, Ermittlungen) oder positiv (Schutz/Prävention) ist
- Wenn Gruppe als Täter, Verdächtiger, Beschuldigter, Gefahr, Unterstützer von Gewalt oder Legitimierer von Terrorismus erscheint → CRIME_FRAME_NEG
- Wenn Krieg, geopolitische Konflikte, militärische Ereignisse oder der Einsatz von Bomben, Raketen oder nuklearen Waffen im Kriegskontext vorkommen → NO_CRIME_FRAME
- Wenn fiktionale, kulturelle oder satirische Darstellungen wie TV-Shows, Filme, Serien oder Karikaturen vorkommen → NO_CRIME_FRAME
- Wenn Demonstrationen, Proteste oder Kundgebungen nur als politische Meinungsäußerung beschrieben werden → NO_CRIME_FRAME
- Wenn Demonstrationen, Proteste oder Kundgebungen ausdrücklich zu konkreten gesetzlichen, politischen, polizeilichen oder präventiven Sicherheitsänderungen führen → CRIME_FRAME_POS
- Wenn Sicherheit, Prävention oder Differenzierung im Vordergrund steht → CRIME_FRAME_POS
- Wenn unklar oder widersprüchlich → UNCLEAR

Im Zweifelsfall:
Fragen Sie sich, ob ein Leser die Gruppe als kriminell, verdächtig, sicherheitsgefährdend, gewaltunterstützend oder als Sicherheitsfaktor wahrnehmen würde. Wenn nein → NO_CRIME_FRAME."""

reminder = "Vergeben Sie genau ein Label: NO_CRIME_FRAME, CRIME_FRAME_NEG oder CRIME_FRAME_POS. Achten Sie besonders darauf, dass die Gruppe explizit mit Kriminalität, Sicherheit, Terrorismus, Gewaltlegitimation, Verdacht, Ermittlungen oder Prävention verknüpft ist. Wenn Kriminalität erwähnt wird, aber nicht mit der Gruppe verbunden ist oder die Gruppe Opfer ist, vergeben Sie NO_CRIME_FRAME. Mutmaßungen, Verdacht oder Ermittlungen zählen als CRIME_FRAME_NEG, wenn die Gruppe explizit mit der mutmaßlichen Straftat verbunden wird. Kriegskontexte, fiktionale Inhalte und bloße Demonstrationen ohne Sicherheits- oder Präventionsbezug sind NO_CRIME_FRAME."

def annotate(text, instructions, reminder, api_key, HOST, MODEL, temperature=0.0):
    """Send a paragraph to the API for annotation."""
    prompt = f"{instructions}\n\nNow annotate this paragraph:\n\n{text}\n\n{reminder}\n\nRespond in this format exactly:\nLabel: <NO_CRIME_FRAME or CRIME_FRAME_NEG or CRIME_FRAME_POS>\nExplanation: <one sentence explaining your choice>"

    payload = {
        "model": MODEL,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": "Sie sind ein Experte für Inhaltsanalyse. Befolgen Sie die Annotationsanweisungen genau und antworten Sie immer im angegebenen Format."},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for attempt in range(3):
        try:
            response = requests.post(
                f"{HOST}/chat/completions",
                json=payload,
                headers=headers,
                timeout=120
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                print(f"  [attempt {attempt+1}] Status {response.status_code}")
        except Exception as e:
            print(f"  [attempt {attempt+1}] Error: {e}")
            time.sleep(5)
    return "ERROR"


def parse_label(raw_output):
    """Extract and normalize label from raw model output.
    Handles misspellings and label drift from small LLMs.
    """
    raw_upper = raw_output.upper()

    # Check NO_CRIME_FRAME first because it contains CRIME_FRAME
    if "NO_CRIME_FRAME" in raw_upper or "NO CRIME FRAME" in raw_upper:
        return "NO_CRIME_FRAME"
    elif "CRIME_FRAME_NEG" in raw_upper or "CRIME FRAME NEG" in raw_upper:
        return "CRIME_FRAME_NEG"
    elif "CRIME_FRAME_POS" in raw_upper or "CRIME FRAME POS" in raw_upper:
        return "CRIME_FRAME_POS"
    else:
        return "UNCLEAR"


def parse_explanation(raw_output):
    """Extract explanation sentence from raw model output."""
    for line in raw_output.split("\n"):
        if line.lower().startswith("explanation:"):
            return line[len("explanation:"):].strip()
    return raw_output
