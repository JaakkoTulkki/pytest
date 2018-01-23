# -*- coding: utf-8 -*-

from .language import Language


class Spanish(Language):
    def get_summary_stats(self, line, session_duration):
        return "%s en %.2f %s" % (line, session_duration, self.get_seconds())

    def get_test_result_translation(self, result):
        return {
            'skipped': 'omitido',
            'passed': 'pasado',
            'failed': 'fallado'
        }[result]

    def get_seconds(self):
        return "segundos"

    def get_skipped_lower(self):
        return "omitido"

    def get_test_session(self):
        return u"sesión de prueba"

    def get_platform(self):
        return 'plataforma'

    def get_errors_lower(self):
        return "errores"

    def get_plugin_registered(self, plugin):
        return "plugin registreado"

    def get_errors_setup(self):
        return u"ERROR en la preparación de"

    def get_errors_collecting(self):
        return u"ERROR en la colección de"

    def no_tests_ran(self):
        return u"No se ejecutó ninguna prueba"

    def get_internal_error(self):
        return "ERROR INTERNO"

    def get_session_starts(self):
        return u"comienza la sesión de prueba"

    def get_item(self):
        return u"ítem"

    def get_passes(self):
        return "PASA"

    def get_undetermined_location(self):
        return u"ubicación indeterminada"

    def get_colletion_failures(self):
        return u"fallas de colección"

    def get_errors_teardown(self):
        return "ERROR en el desmontaje de"

    def get_show_traceback_instructions(self):
        return "usa --fulltrace para mostrar un rastreo completo con KeyboardInterrupt"

    def get_error_lower(self):
        return 'error'

    def get_warnings_summary(self):
        return "resumen de advertencias"

    def get_collected(self):
        return 'coleccionado'

    def get_summary_stats_translations(self):
        return {'skipped': 'omitido', 'warnings': 'advertencias', 'xfailed': 'xfailed', 'xpassed': 'xpassed',
                'failed': 'fallado', 'deselected': 'deseleccionado', 'passed': 'pasado', 'error': 'error'}

    def get_item_plural(self):
        return u"ítems"

    def get_collecting(self):
        return 'coleccionando'

    def get_errors(self):
        return 'ERRORES'

    def get_failures(self):
        return 'FALLADOS'

    def get_tests_deselected(self):
        return "pruebas deseleccionadas"
