from datetime import datetime
from typing import List, Dict
from duckduckgo_search import DDGS
import os
import sys
import Orange
from Orange.widgets.widget import Input, Output
from AnyQt.QtWidgets import QApplication, QPushButton
import json

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management, base_widget
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import convert
else:
    from orangecontrib.AAIT.utils import thread_management, base_widget
    from orangecontrib.HLIT_dev.remote_server_smb import convert

class WebSearch(base_widget.BaseListWidget):
    name = "WebSearch"
    description = "Search url website from a query with DDG."
    icon = "icons/websearch.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/websearch.png"
    priority = 3000
    gui = ""
    want_control_area = False
    category = "AAIT - TOOLBOX"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owwebsearch.ui")

    class Inputs:
        data = Input("Data", Orange.data.Table)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if in_data is None:
            return
        if self.data:
            self.var_selector.add_variables(self.data.domain)
            self.var_selector.select_variable_by_name(self.selected_column_name)
        self.run()

    class Outputs:
        data = Output("Data", Orange.data.Table)


    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(500)
        self.setFixedHeight(500)

        self.max_results = 20
        self.region = 'fr-fr'
        self.time_range = 'y'
        self.relevance_threshold = 0.3

        self.pushButton_run =self.findChild(QPushButton, 'pushButton_send')
        self.pushButton_run.clicked.connect(self.run)
        self.load_config()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../utils/config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.domain_context = config["domain_context"]
        self.stop_words = set(config["stop_words"])

    def detect_domain(self, query: str):
        """Détecte les domaines dans la requête"""
        query_lower = query.lower()
        detected = []

        for domain_key in self.domain_context.keys():
            if domain_key in query_lower:
                detected.append(domain_key)

        return detected

    def get_contextual_terms(self, query: str):
        """Récupère les termes contextuels basés sur le domaine"""
        domains = self.detect_domain(query)

        if not domains:
            return []

        context_terms = []
        for domain in domains:
            terms = self.domain_context.get(domain, [])[:3]
            context_terms.extend(terms)

        return context_terms

    def optimize_query(self, query: str):
        """Génère des variations optimisées de la requête"""
        variations = []

        words = query.split()
        important_words = [
            w for w in words
            if len(w) > 3 and w.lower() not in self.stop_words
        ]

        # Query avec guillemets
        if important_words:
            quoted_query = query
            for word in important_words[:2]:
                quoted_query = quoted_query.replace(word, f'"{word}"')
            if quoted_query != query:
                variations.append(quoted_query)

        # Query enrichie avec contexte
        context_terms = self.get_contextual_terms(query)
        if context_terms:
            enriched = f"{query} {' '.join(context_terms[:3])}"
            variations.append(enriched)

        # Query simplifiée
        simple_words = [w for w in words if w.lower() not in self.stop_words]
        if len(simple_words) >= 2:
            simplified = ' '.join(simple_words)
            if simplified != query:
                variations.append(simplified)

        # Query originale
        variations.append(query)

        # Dédupliquer
        seen = set()
        unique_variations = []
        for v in variations:
            if v not in seen:
                seen.add(v)
                unique_variations.append(v)

        return unique_variations

    def calculate_relevance(self, query: str, title: str, snippet: str):
        """Calcule un score de pertinence"""
        query_lower = query.lower()
        title_lower = title.lower()
        snippet_lower = snippet.lower()

        query_words = [
            w for w in query_lower.split()
            if len(w) > 3 and w not in self.stop_words
        ]

        if not query_words:
            return 0.5

        score = 0.0
        max_score = len(query_words)

        for word in query_words:
            if word in title_lower:
                score += 0.6
            elif word in snippet_lower:
                score += 0.4
            else:
                word_norm = self.normalize_text(word)
                title_norm = self.normalize_text(title_lower)
                snippet_norm = self.normalize_text(snippet_lower)

                if word_norm in title_norm:
                    score += 0.5
                elif word_norm in snippet_norm:
                    score += 0.3

        return min(score / max_score, 1.0)

    def normalize_text(self, text: str):
        """Normalise le texte"""
        accent_map = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'î': 'i', 'ï': 'i',
            'ô': 'o', 'ö': 'o',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }

        result = text.lower()
        for old, new in accent_map.items():
            result = result.replace(old, new)

        return result

    def filter_by_relevance(self, results: List[Dict], query: str):
        scored_results = []

        for result in results:
            score = self.calculate_relevance(
                query,
                result.get('title', ''),
                result.get('body', result.get('snippet', ''))
            )
            result['relevance_score'] = score
            scored_results.append(result)

        filtered = [r for r in scored_results if r['relevance_score'] >= self.relevance_threshold]
        filtered.sort(key=lambda x: x['relevance_score'], reverse=True)

        return filtered

    def search(self, use_optimization: bool = True):
        all_results = []
        seen_urls = set()

        if use_optimization:
            query_variations = self.optimize_query(self.query)
            queries_to_try = query_variations
        else:
            queries_to_try = [self.query]

        for idx, q in enumerate(queries_to_try, 1):
            if len(all_results) >= self.max_results:
                break

            try:
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(
                        q,
                        region=self.region,
                        safesearch='off',
                        timelimit=self.time_range,
                        max_results=min(50, self.max_results * 3)
                    ))
                    filtered = self.filter_by_relevance(search_results, self.query)

                    new_count = 0
                    for r in filtered:
                        if r['href'] not in seen_urls:
                            seen_urls.add(r['href'])

                            result = {
                                'url': r['href'],
                                'title': r['title'],
                                'snippet': r.get('body', ''),
                                'source': 'DuckDuckGo',
                                'query': self.query,
                                'query_variation': q,
                                'relevance_score': r['relevance_score'],
                                'fetched_at': datetime.now().isoformat(),
                                'rank': len(all_results) + 1
                            }

                            all_results.append(result)
                            new_count += 1

                            if len(all_results) >= self.max_results:
                                break

            except Exception as e:
                print(e)
                continue

        return all_results[:self.max_results]

    def run(self):
        self.error("")
        self.warning("")
        if self.data is None:
            return

        if not self.selected_column_name in self.data.domain:
            self.warning(f'Previously selected column "{self.selected_column_name}" does not exist in your data.')
            return

        self.query = self.data.get_column(self.selected_column_name)[0]

        self.progressBarInit()
        self.thread = thread_management.Thread(self.search)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def handle_progress(self, progress) -> None:
        value = progress[0]
        text = progress[1]
        if value is not None:
            self.progressBarSet(value)
        if text is None:
            self.textBrowser.setText("")
        else:
            self.textBrowser.insertPlainText(text)

    def handle_result(self, result):
        if result is None or len(result) == 0:
            self.Outputs.data.send(None)
            return
        data = convert.convert_json_implicite_to_data_table(result)
        self.Outputs.data.send(data)
        self.data = None

    def handle_finish(self):
        print("Generation finished")
        self.progressBarFinished()

    def post_initialized(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = WebSearch()
    my_widget.show()

    if hasattr(app, "exec"):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())