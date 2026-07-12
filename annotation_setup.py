import time
import requests

VALID_LABELS = ["NO_CRIME_FRAME", "CRIME_FRAME_NEG", "CRIME_FRAME_POS"]

instructions = """Sie sind ein Experte für Inhaltsanalyse in einer Studie zur medialen Darstellung ethnischer und sozialer Gruppen in deutschen Nachrichten. Ihre Aufgabe ist es, zu klassifizieren, ob ein gegebener Nachrichtenabsatz einen Einwanderungs- und Kriminalitätsrahmen enthält und, falls ja, ob dieser negativ (Bedrohung) oder positiv (Sicherheitsgewinn/Prävention) dargestellt wird.

Sie erhalten Mehrfachabsätze aus deutschen Zeitungsartikeln. Es können mehrere Gruppen erwähnt werden. Gruppen können als [Gruppe 1] oder [andere Gruppe] bezeichnet werden. Kodieren Sie ausschließlich die Darstellung von [Gruppe 1]. Erwähnungen anderer Gruppen dienen lediglich als Kontext und dürfen Ihre Entscheidung nicht beeinflussen, sofern sie nicht ausdrücklich auf [Gruppe 1] bezogen werden. Konzentrieren Sie sich ausschließlich auf das, was explizit im Text steht. Schließen Sie keine Gruppenassoziationen, die nicht direkt ausgedrückt werden.

Der Kriminalitäts- oder Sicherheitsrahmen muss einen Bezug zu Deutschland haben. Ein Deutschlandbezug liegt auch vor, wenn Entscheidungen, Maßnahmen oder Bedrohungen auf Ebene der Europäischen Union oder der NATO beschrieben werden und Deutschland als Mitglied davon betroffen ist. Die bloße Erwähnung der EU oder NATO reicht nicht aus. Es muss erkennbar sein, dass die Entscheidung, Maßnahme oder Bedrohung auch Deutschland oder die gemeinsame Sicherheit der Mitgliedstaaten betrifft.

WICHTIG:
Ein Kriminalitäts- oder Sicherheitsrahmen liegt nur dann vor, wenn [Gruppe 1] explizit mit Kriminalität, Sicherheit, Gefahr, Gewalt, Terrorismus, Verdacht, Ermittlungen oder Prävention verknüpft wird. Andere im Absatz erwähnte Gruppen sind für die Klassifikation nicht relevant.

Zusätzlich muss ein Bezug zu Deutschland, zu deutschen Behörden oder Institutionen, zur deutschen Bevölkerung oder zur Sicherheit Deutschlands bestehen. Ein Deutschlandbezug liegt auch vor, wenn der Täter oder das Opfer aus Deutschland kommt oder die deutsche Staatsangehörigkeit besitzt. Auch ein Bezug zur EU oder NATO zählt, wenn Deutschland durch eine gemeinsame Entscheidung, Maßnahme oder Bedrohung als Mitglied betroffen ist. Ein rein ausländisches Ereignis ohne erkennbaren Deutschland-, EU- oder NATO-Bezug erhält NO_CRIME_FRAME.

NO_CRIME_FRAME:
Ein Absatz erhält dieses Label, wenn kein expliziter Kriminalitäts- oder Sicherheitsrahmen vorliegt. Dies gilt insbesondere wenn:
- [Gruppe 1] gar nicht erwähnt wird
- Kriminalität erwähnt wird, aber nicht mit [Gruppe 1] verknüpft ist
- Ausschließlich eine andere Gruppe als [Gruppe 1] mit Kriminalität oder Sicherheit verknüpft wird
- [Gruppe 1] als Opfer von Straftaten dargestellt wird und kein kriminelles Verhalten zeigt
- Kriminalität auf soziale Bedingungen (Armut, Ausgrenzung etc.) zurückgeführt wird
- Der Text Kriminalitätszuschreibungen relativiert oder widerspricht („kein Generalverdacht“, „nicht alle“)
- Krieg, geopolitische Konflikte oder militärische Ereignisse beschrieben werden
- Der Einsatz von Bomben, Luftangriffen, Raketen, Drohnen, Atomwaffen oder nuklearen Waffen im Kontext von Krieg, Militär, geopolitischen Konflikten oder staatlicher Kriegsführung beschrieben wird
- Humanitäre Krisen oder Naturkatastrophen beschrieben werden
- Ein Täter erwähnt wird, aber NICHT Mitglied von [Gruppe 1] ist
- Fiktionale, kulturelle oder satirische Darstellungen beschrieben werden, z.B. TV-Shows, Filme, Serien, Romane, Theaterstücke, Comics, Karikaturen oder Kunstwerke, solange [Gruppe 1] nicht als reale kriminelle oder sicherheitsgefährdende Akteurin dargestellt wird
- Demonstrationen, Proteste, Kundgebungen oder politische Versammlungen erwähnt werden, aber nicht mit Kriminalität, Gewalt, Sicherheitsbedrohung, Prävention oder konkreten sicherheitsbezogenen Maßnahmen verknüpft sind
- Wenn Kriminalität, Gewalt oder Bedrohung nur als Propaganda, falsches Narrativ, Diffamierung oder unbelegte Zuschreibung gegen [Gruppe 1] erwähnt wird und der Text diese Darstellung als manipulativ oder falsch einordnet, vergeben Sie NO_CRIME_FRAME. In solchen Fällen wird [Gruppe 1] als Ziel oder Opfer der Zuschreibung dargestellt, nicht als tatsächlicher Täter oder Sicherheitsrisiko.
- Wenn ein Ereignis ausschließlich im Ausland stattfindet und weder Deutschland noch deutsche Behörden, deutsche Institutionen, deutsche Staatsangehörige oder die Sicherheit Deutschlands ausdrücklich betroffen sind. Ein Bezug zur EU oder NATO zählt nur, wenn Deutschland als Mitglied von der beschriebenen Entscheidung, Maßnahme oder Bedrohung betroffen ist.
- Wenn die EU oder NATO nur beiläufig erwähnt wird, ohne dass eine konkrete gemeinsame Sicherheitsentscheidung, Maßnahme oder Bedrohung beschrieben wird, die Deutschland als Mitglied betrifft

WICHTIG: NO_CRIME_FRAME nur vergeben, wenn [Gruppe 1] eindeutig als Opfer dargestellt wird und nicht selbst mit kriminellem Verhalten, Verdacht, Ermittlungen, Gewaltunterstützung oder Sicherheitsgefahr in Verbindung steht. Wenn ein Mitglied von [Gruppe 1] eine Straftat begeht, mutmaßlich begeht, verdächtigt wird oder daran beteiligt ist, bleibt dies CRIME_FRAME_NEG – auch dann, wenn die Handlung durch äußeren Druck, Anreize oder vermeintliche Vorteile (z.B. schnellerer Erhalt von Papieren) motiviert ist.

Ein solcher Fall erhält jedoch nur dann CRIME_FRAME_NEG, wenn zusätzlich ein Bezug zu Deutschland besteht. Ein Deutschlandbezug liegt auch vor, wenn der Täter oder das Opfer aus Deutschland kommt oder die deutsche Staatsangehörigkeit besitzt, deutsche Behörden beteiligt sind, die Tat Deutschland betrifft oder eine EU- oder NATO-Maßnahme beschrieben wird, die Deutschland als Mitglied mitbetrifft.

CRIME_FRAME_NEG:
Ein Absatz erhält dieses Label, wenn [Gruppe 1] als Quelle von Kriminalität oder Sicherheitsbedrohung dargestellt wird. Dies umfasst:
- [Gruppe 1] oder ein Mitglied von [Gruppe 1] wird als Täter, Verdächtiger, Beschuldigter oder kriminell dargestellt
- [Gruppe 1] oder ein Mitglied von [Gruppe 1] wird mit konkreten Straftaten verbunden (z.B. Diebstahl, Gewalt, Mord)
- Asylmissbrauch oder erschlichene Asylleistungen, sofern [Gruppe 1] oder ein Mitglied von [Gruppe 1] ausdrücklich mit strafbarem oder betrügerischem Verhalten verbunden wird
- [Gruppe 1] wird als Ursache steigender Kriminalität dargestellt
- [Gruppe 1] wird als Gefahr für öffentliche oder nationale Sicherheit dargestellt
- [Gruppe 1] wird als Gefahr für die Sicherheit Deutschlands oder der Europäischen Union dargestellt
- Migration oder die Zugehörigkeit zu [Gruppe 1] wird mit Kriminalität verknüpft
- Terrorismus oder Extremismus wird mit [Gruppe 1] verbunden
- Physische Gewalt oder Bedrohung geht explizit von Mitgliedern von [Gruppe 1] aus
- [Gruppe 1] begrüßt, legitimiert, feiert, rechtfertigt oder unterstützt einen Anschlag, Terrorakt, Gewaltakt oder eine Straftat
- [Gruppe 1] stellt einen Anschlag, Terrorakt, Gewaltakt oder eine Straftat als Widerstand, heroische Operation oder legitime Handlung dar
- [Gruppe 1] erscheint als Unterstützer, Kommentator, ideologischer Bezugspunkt oder politischer Akteur, der explizit mit Zustimmung, Rechtfertigung, Feier, Unterstützung oder ideologischer Nähe zu Terrorismus, politischer Gewalt oder Straftaten verbunden wird
- Mutmaßungen, Verdachtsfälle, Ermittlungen, Beschuldigungen oder noch nicht gerichtlich bestätigte Vorwürfe zählen als CRIME_FRAME_NEG, wenn [Gruppe 1] oder ein Mitglied von [Gruppe 1] explizit mit der mutmaßlichen Straftat, dem Verdacht oder den Ermittlungen verknüpft wird. Dies gilt auch bei Formulierungen wie „mutmaßlich“, „verdächtigt“, „beschuldigt“, „soll getan haben“, „laut Polizei“, „Ermittlungen gegen“ oder „unter Verdacht“
- Polizeiliche Maßnahmen gegen ein Mitglied von [Gruppe 1], z.B. Festnahme, Durchsuchung, Fahndung, Ermittlungen, Drogentest oder Anklage, sind CRIME_FRAME_NEG, wenn das Gruppenmitglied als Täter, Verdächtiger, Beschuldigter oder Gesuchter erscheint
- Achtung: Die Bezeichnung „illegale Einwanderer“ fällt nicht unter diesen Topos, wenn nicht noch weitere Verbrechen genannt werden. Schleuser aus [Gruppe 1], die als Kriminelle dargestellt werden, zählen aber als CRIME_FRAME_NEG
- Eine deutsche Behörde, Institution oder Amtsperson stellt [Gruppe 1] ausdrücklich als Kriminalitätsproblem oder Sicherheitsrisiko für Deutschland dar
- [Gruppe 1] oder Migration wird als Ursache von Gewalt, Chaos, Kontrollverlust oder gesellschaftlicher Bedrohung in Deutschland dargestellt
- Ein Mitglied von [Gruppe 1] übt in Deutschland Zwang, Drohung oder autoritäre Kontrolle aus, z.B. wenn Mädchen an deutschen Schulen zum Tragen eines Kopftuchs gezwungen werden
- Eine Straftat oder ein Anschlag im Ausland wird mit Deutschland verbunden, z.B. weil der Täter oder das Opfer aus Deutschland kommt, in Deutschland lebt oder lebte, die deutsche Staatsangehörigkeit besitzt, deutsche Behörden beteiligt sind oder deutsche Ziele betroffen sind
- Eine Institution der EU oder NATO stellt [Gruppe 1] als Sicherheitsrisiko dar oder beschließt eine sicherheitsbezogene Maßnahme, die Deutschland als Mitglied betrifft
- Eine Bedrohung richtet sich gegen die EU, die NATO oder deren Mitgliedstaaten und betrifft damit auch die gemeinsame Sicherheit Deutschlands

WICHTIG: [Gruppe 1] muss klar mit der Straftat, Bedrohung, Gewaltlegitimation, dem Verdacht, den Ermittlungen oder der Sicherheitsgefahr verknüpft sein. Reine Erwähnung von Kriminalität reicht nicht. Eine gerichtliche Bestätigung oder Verurteilung ist nicht erforderlich. Eine direkte Verantwortung oder Täterschaft von [Gruppe 1] ist nicht zwingend erforderlich, wenn [Gruppe 1] den Gewaltakt ausdrücklich legitimiert, begrüßt, feiert oder unterstützt. Zusätzlich muss ein Deutschlandbezug bestehen. Dieser liegt auch vor, wenn Täter oder Opfer aus Deutschland kommen oder die deutsche Staatsangehörigkeit besitzen oder wenn Deutschland durch Maßnahmen oder Bedrohungen der EU oder NATO als Mitglied betroffen ist.

CRIME_FRAME_POS:
Ein Absatz erhält dieses Label, wenn ein Sicherheits- oder Kriminalitätsrahmen vorhanden ist, aber positiv dargestellt wird. Dies umfasst:
- Maßnahmen zur Kriminalitätsbekämpfung im Zusammenhang mit [Gruppe 1]
- Prävention im Zusammenhang mit [Gruppe 1] (z.B. soziale Arbeit, Integration, Deradikalisierung)
- Differenzierung in Bezug auf [Gruppe 1] („kein Generalverdacht“, „nicht alle“)
- Kriminalität wird durch soziale Faktoren erklärt statt durch [Gruppe 1] selbst
- Mitglieder von [Gruppe 1] wirken aktiv an Sicherheit oder Prävention mit (z.B. Polizei, Sozialarbeit)
- Maßnahmen werden als Verbesserung von Sicherheit oder Ordnung dargestellt
- Maßnahmen der EU oder NATO gelten ebenfalls als CRIME_FRAME_POS, wenn sie ausdrücklich der Sicherheit Deutschlands oder der gemeinsamen Sicherheit der Mitgliedstaaten dienen
- Demonstrationen, Proteste oder Kundgebungen sind nur dann CRIME_FRAME_POS, wenn sie ausdrücklich zu konkreten gesetzlichen, politischen, polizeilichen oder präventiven Änderungen führen oder als Beitrag zu mehr Sicherheit, Schutz, Prävention oder Rechtsstaatlichkeit dargestellt werden
- Abgrenzung zu CRIME_FRAME_NEG: Polizeiliche Maßnahmen gegen ein Mitglied von [Gruppe 1] (z.B. Festnahme, Ermittlungen, Drogentest) sind CRIME_FRAME_NEG, wenn das Gruppenmitglied als Täter, Verdächtiger, Beschuldigter oder Gesuchter erscheint. CRIME_FRAME_POS nur vergeben, wenn Schutz, Prävention, Differenzierung oder Sicherheitsgewinn im Vordergrund steht.
- Präventions- oder Schutzmaßnahmen im Ausland zählen nur dann, wenn ein ausdrücklicher Bezug zu Deutschland oder zu einer gemeinsamen Sicherheitsmaßnahme der EU oder NATO besteht

Entscheidungsregeln:
- Prüfen Sie zuerst, ob [Gruppe 1] überhaupt mit einem Kriminalitäts- oder Sicherheitsrahmen verknüpft wird
- Wenn nein → NO_CRIME_FRAME
- Prüfen Sie anschließend, ob ein Deutschlandbezug besteht. Ein Bezug zur EU oder NATO zählt nur, wenn Deutschland als Mitglied von der beschriebenen Entscheidung, Maßnahme oder Bedrohung betroffen ist. Ein Deutschlandbezug liegt auch vor, wenn der Täter oder das Opfer aus Deutschland kommt oder die deutsche Staatsangehörigkeit besitzt
- Wenn kein Deutschland-, EU- oder NATO-Bezug besteht → NO_CRIME_FRAME
- Wenn ja → prüfen, ob die Darstellung negativ (Bedrohung, Täterschaft, Verdacht, Ermittlungen) oder positiv (Schutz/Prävention) ist
- Wenn [Gruppe 1] als Täter, Verdächtiger, Beschuldigter, Gefahr, Unterstützer von Gewalt oder Legitimierer von Terrorismus erscheint → CRIME_FRAME_NEG
- Wenn Krieg, geopolitische Konflikte, militärische Ereignisse oder der Einsatz von Bomben, Raketen oder nuklearen Waffen im Kriegskontext vorkommen → NO_CRIME_FRAME
- Wenn fiktionale, kulturelle oder satirische Darstellungen wie TV-Shows, Filme, Serien oder Karikaturen vorkommen → NO_CRIME_FRAME
- Wenn Demonstrationen, Proteste oder Kundgebungen nur als politische Meinungsäußerung beschrieben werden → NO_CRIME_FRAME
- Wenn Demonstrationen, Proteste oder Kundgebungen ausdrücklich zu konkreten gesetzlichen, politischen, polizeilichen oder präventiven Sicherheitsänderungen führen → CRIME_FRAME_POS
- Wenn Sicherheit, Prävention oder Differenzierung im Vordergrund steht → CRIME_FRAME_POS
- Wenn unklar oder widersprüchlich → UNCLEAR

Im Zweifelsfall:
Fragen Sie sich, ob ein Leser [Gruppe 1] als kriminell, verdächtig, sicherheitsgefährdend, gewaltunterstützend oder als Sicherheitsfaktor für Deutschland wahrnehmen würde. Erwähnungen anderer Gruppen dürfen diese Entscheidung nicht beeinflussen. Berücksichtigen Sie auch Fälle, in denen Täter oder Opfer aus Deutschland kommen oder die deutsche Staatsangehörigkeit besitzen. Berücksichtigen Sie außerdem Entscheidungen, Maßnahmen oder Bedrohungen auf Ebene der EU oder NATO, wenn Deutschland als Mitglied davon betroffen ist. Wenn kein erkennbarer Deutschland-, EU- oder NATO-Bezug vorliegt → NO_CRIME_FRAME. Wenn nein → NO_CRIME_FRAME."""
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
