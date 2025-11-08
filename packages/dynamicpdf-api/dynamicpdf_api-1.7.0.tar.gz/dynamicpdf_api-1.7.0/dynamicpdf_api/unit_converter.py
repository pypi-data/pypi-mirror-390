from .page_size import PageSize

class UnitConverter:

    @staticmethod
    def inches_to_points(size):
        '''
        Method to convert inches to point

        Args:
            size (integer): Size in inches.

        Returns:
            Size in points.
        '''
        return size * 72.0

    @staticmethod
    def millimeters_to_points(size):
        '''
        Method to convert millimeters to point

        Args:
            size (integer): Size in millimeters.

        Returns:
            Size in points.
        '''
        return size * 2.8346456692913385826771653543307

    @staticmethod
    def _get_paper_size(size):
        switcher = {
            PageSize.Letter: (UnitConverter.inches_to_points(8.5), UnitConverter.inches_to_points(11)),
            PageSize.Legal: (UnitConverter.inches_to_points(8.5), UnitConverter.inches_to_points(14)),
            PageSize.Executive: (UnitConverter.inches_to_points(7.25), UnitConverter.inches_to_points(10.5)),
            PageSize.Tabloid: (UnitConverter.inches_to_points(11), UnitConverter.inches_to_points(17)),
            PageSize.Envelope10: (UnitConverter.inches_to_points(4.125), UnitConverter.inches_to_points(9.5)),
            PageSize.EnvelopeMonarch: (UnitConverter.inches_to_points(3.875), UnitConverter.inches_to_points(7.5)),
            PageSize.Folio: (UnitConverter.inches_to_points(8.5), UnitConverter.inches_to_points(13)),
            PageSize.Statement: (UnitConverter.inches_to_points(5.5), UnitConverter.inches_to_points(8.5)),
            PageSize.A4: (UnitConverter.millimeters_to_points(210), UnitConverter.millimeters_to_points(297)),
            PageSize.A5: (UnitConverter.millimeters_to_points(148), UnitConverter.millimeters_to_points(210)),
            PageSize.B4: (UnitConverter.millimeters_to_points(250), UnitConverter.millimeters_to_points(353)),
            PageSize.B5: (UnitConverter.millimeters_to_points(176), UnitConverter.millimeters_to_points(250)),
            PageSize.A3: (UnitConverter.millimeters_to_points(297), UnitConverter.millimeters_to_points(420)),
            PageSize.B3: (UnitConverter.millimeters_to_points(353), UnitConverter.millimeters_to_points(500)),
            PageSize.A6: (UnitConverter.millimeters_to_points(105), UnitConverter.millimeters_to_points(148)),
            PageSize.B5JIS: (UnitConverter.millimeters_to_points(182), UnitConverter.millimeters_to_points(257)),
            PageSize.EnvelopeDL: (UnitConverter.millimeters_to_points(110), UnitConverter.millimeters_to_points(220)),
            PageSize.EnvelopeC5: (UnitConverter.millimeters_to_points(162), UnitConverter.millimeters_to_points(229)),
            PageSize.EnvelopeB5: (UnitConverter.millimeters_to_points(176), UnitConverter.millimeters_to_points(250)),
            PageSize.PRC16K: (UnitConverter.millimeters_to_points(146), UnitConverter.millimeters_to_points(215)),
            PageSize.PRC32K: (UnitConverter.millimeters_to_points(97), UnitConverter.millimeters_to_points(151)),
            PageSize.Quatro: (UnitConverter.millimeters_to_points(215), UnitConverter.millimeters_to_points(275)),
            PageSize.DoublePostcard: (UnitConverter.millimeters_to_points(148.0), UnitConverter.millimeters_to_points(200.0)),
            PageSize.Postcard: (UnitConverter.inches_to_points(3.94), UnitConverter.inches_to_points(5.83))
        }
        return switcher.get(size, (UnitConverter.inches_to_points(8.5), UnitConverter.inches_to_points(11)))
