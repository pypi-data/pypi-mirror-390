import datetime

import pytest

from dekad import Dekad, dekad_range


class TestDekadConstruction:
    """Test Dekad construction and factory methods."""

    def test_init_valid(self):
        dekad = Dekad(2024, 15)
        assert dekad.year == 2024
        assert dekad.dekad_of_year == 15

    def test_init_invalid_year(self):
        with pytest.raises(ValueError, match='Year must be positive'):
            Dekad(0, 15)
        with pytest.raises(ValueError, match='Year must be positive'):
            Dekad(-1, 15)

    def test_init_invalid_dekad_of_year(self):
        with pytest.raises(
            ValueError, match='Dekad of year must be between 1 and 36'
        ):
            Dekad(2024, 0)
        with pytest.raises(
            ValueError, match='Dekad of year must be between 1 and 36'
        ):
            Dekad(2024, 37)

    def test_from_date_first_dekad(self):
        date = datetime.date(2024, 5, 1)
        dekad = Dekad.from_date(date)
        assert dekad.year == 2024
        assert dekad.month == 5
        assert dekad.dekad_of_month == 1
        assert dekad.dekad_of_year == 13

    def test_from_date_second_dekad(self):
        date = datetime.date(2024, 5, 15)
        dekad = Dekad.from_date(date)
        assert dekad.year == 2024
        assert dekad.month == 5
        assert dekad.dekad_of_month == 2
        assert dekad.dekad_of_year == 14

    def test_from_date_third_dekad(self):
        date = datetime.date(2024, 5, 25)
        dekad = Dekad.from_date(date)
        assert dekad.year == 2024
        assert dekad.month == 5
        assert dekad.dekad_of_month == 3
        assert dekad.dekad_of_year == 15

    def test_from_date_boundaries(self):
        # Day 10 should be in first dekad
        assert Dekad.from_date(datetime.date(2024, 3, 10)).dekad_of_month == 1
        # Day 11 should be in second dekad
        assert Dekad.from_date(datetime.date(2024, 3, 11)).dekad_of_month == 2
        # Day 20 should be in second dekad
        assert Dekad.from_date(datetime.date(2024, 3, 20)).dekad_of_month == 2
        # Day 21 should be in third dekad
        assert Dekad.from_date(datetime.date(2024, 3, 21)).dekad_of_month == 3

    def test_from_ymd_valid(self):
        dekad = Dekad.from_ymd(2024, 5, 2)
        assert dekad.year == 2024
        assert dekad.month == 5
        assert dekad.dekad_of_month == 2
        assert dekad.dekad_of_year == 14

    def test_from_ymd_invalid_month(self):
        with pytest.raises(ValueError, match='Month must be between 1 and 12'):
            Dekad.from_ymd(2024, 0, 2)
        with pytest.raises(ValueError, match='Month must be between 1 and 12'):
            Dekad.from_ymd(2024, 13, 2)

    def test_from_ymd_invalid_dekad_of_month(self):
        with pytest.raises(
            ValueError, match='Dekad of month must be between 1 and 3'
        ):
            Dekad.from_ymd(2024, 5, 0)
        with pytest.raises(
            ValueError, match='Dekad of month must be between 1 and 3'
        ):
            Dekad.from_ymd(2024, 5, 4)


class TestDekadProperties:
    """Test Dekad properties and derived values."""

    def test_properties(self):
        dekad = Dekad(2024, 15)
        assert dekad.year == 2024
        assert dekad.dekad_of_year == 15
        assert dekad.month == 5
        assert dekad.dekad_of_month == 3

    def test_month_derivation(self):
        # First dekad of January
        assert Dekad(2024, 1).month == 1
        # Last dekad of January
        assert Dekad(2024, 3).month == 1
        # First dekad of February
        assert Dekad(2024, 4).month == 2
        # Last dekad of December
        assert Dekad(2024, 36).month == 12

    def test_dekad_of_month_derivation(self):
        # January dekads
        assert Dekad(2024, 1).dekad_of_month == 1
        assert Dekad(2024, 2).dekad_of_month == 2
        assert Dekad(2024, 3).dekad_of_month == 3
        # February dekads
        assert Dekad(2024, 4).dekad_of_month == 1
        assert Dekad(2024, 5).dekad_of_month == 2
        assert Dekad(2024, 6).dekad_of_month == 3


class TestDekadDateConversion:
    """Test conversion between Dekad and dates."""

    def test_first_date_dekad1(self):
        dekad = Dekad(2024, 13)  # May, dekad 1
        assert dekad.first_date() == datetime.date(2024, 5, 1)

    def test_first_date_dekad2(self):
        dekad = Dekad(2024, 14)  # May, dekad 2
        assert dekad.first_date() == datetime.date(2024, 5, 11)

    def test_first_date_dekad3(self):
        dekad = Dekad(2024, 15)  # May, dekad 3
        assert dekad.first_date() == datetime.date(2024, 5, 21)

    def test_last_date_dekad1(self):
        dekad = Dekad(2024, 13)  # May, dekad 1
        assert dekad.last_date() == datetime.date(2024, 5, 10)

    def test_last_date_dekad2(self):
        dekad = Dekad(2024, 14)  # May, dekad 2
        assert dekad.last_date() == datetime.date(2024, 5, 20)

    def test_last_date_dekad3_31days(self):
        dekad = Dekad(2024, 15)  # May, dekad 3 (31 days)
        assert dekad.last_date() == datetime.date(2024, 5, 31)

    def test_last_date_dekad3_30days(self):
        dekad = Dekad(2024, 12)  # April, dekad 3 (30 days)
        assert dekad.last_date() == datetime.date(2024, 4, 30)

    def test_last_date_dekad3_february_leap_year(self):
        dekad = Dekad(2024, 6)  # February 2024, dekad 3 (leap year)
        assert dekad.last_date() == datetime.date(2024, 2, 29)

    def test_last_date_dekad3_february_non_leap_year(self):
        dekad = Dekad(2023, 6)  # February 2023, dekad 3 (non-leap year)
        assert dekad.last_date() == datetime.date(2023, 2, 28)

    def test_round_trip_conversion(self):
        # Test that converting date -> dekad -> date preserves the dekad range
        date = datetime.date(2024, 5, 15)
        dekad = Dekad.from_date(date)
        assert dekad.first_date() <= date <= dekad.last_date()


class TestDekadArithmetic:
    """Test arithmetic operations on Dekad objects."""

    def test_add_positive(self):
        dekad = Dekad(2024, 15)
        result = dekad + 5
        assert result == Dekad(2024, 20)

    def test_add_negative(self):
        dekad = Dekad(2024, 15)
        result = dekad + (-5)
        assert result == Dekad(2024, 10)

    def test_add_across_year_boundary(self):
        dekad = Dekad(2024, 35)
        result = dekad + 5
        assert result == Dekad(2025, 4)

    def test_radd(self):
        dekad = Dekad(2024, 15)
        result = 5 + dekad
        assert result == Dekad(2024, 20)

    def test_sub_int(self):
        dekad = Dekad(2024, 15)
        result = dekad - 5
        assert result == Dekad(2024, 10)

    def test_sub_dekad(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 10)
        result = dekad1 - dekad2
        assert result == 5

    def test_sub_dekad_negative(self):
        dekad1 = Dekad(2024, 10)
        dekad2 = Dekad(2024, 15)
        result = dekad1 - dekad2
        assert result == -5

    def test_sub_dekad_across_years(self):
        dekad1 = Dekad(2025, 5)
        dekad2 = Dekad(2024, 35)
        result = dekad1 - dekad2
        assert result == 6  # (2025-1)*36 + 5 - ((2024-1)*36 + 35) = 6

    def test_rsub_raises_error(self):
        dekad = Dekad(2024, 15)
        with pytest.raises(
            TypeError, match='Cannot subtract Dekad from integer'
        ):
            _ = 5 - dekad

    def test_add_non_integer_raises_error(self):
        dekad = Dekad(2024, 15)
        with pytest.raises(TypeError, match='Can only add integers to Dekad'):
            _ = dekad + 1.5  # type: ignore[operator]

    def test_sub_invalid_type_raises_error(self):
        dekad = Dekad(2024, 15)
        with pytest.raises(
            TypeError,
            match='Can only subtract integers or Dekad from Dekad',
        ):
            _ = dekad - '5'  # type: ignore[operator]

    def test_add_resulting_in_non_positive_dekad(self):
        dekad = Dekad(1, 1)
        with pytest.raises(
            ValueError, match='Resulting dekad would be non-positive'
        ):
            _ = dekad - 1


class TestDekadComparison:
    """Test comparison operations on Dekad objects."""

    def test_equality(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 15)
        assert dekad1 == dekad2

    def test_inequality(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 16)
        assert dekad1 != dekad2

    def test_less_than(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 16)
        assert dekad1 < dekad2
        assert not dekad2 < dekad1

    def test_less_than_different_years(self):
        dekad1 = Dekad(2023, 36)
        dekad2 = Dekad(2024, 1)
        assert dekad1 < dekad2

    def test_less_than_or_equal(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 16)
        dekad3 = Dekad(2024, 15)
        assert dekad1 <= dekad2
        assert dekad1 <= dekad3
        assert not dekad2 <= dekad1

    def test_greater_than(self):
        dekad1 = Dekad(2024, 16)
        dekad2 = Dekad(2024, 15)
        assert dekad1 > dekad2
        assert not dekad2 > dekad1

    def test_greater_than_or_equal(self):
        dekad1 = Dekad(2024, 16)
        dekad2 = Dekad(2024, 15)
        dekad3 = Dekad(2024, 16)
        assert dekad1 >= dekad2
        assert dekad1 >= dekad3
        assert not dekad2 >= dekad1

    def test_comparison_with_non_dekad(self):
        dekad = Dekad(2024, 15)
        assert dekad != 'not a dekad'
        assert dekad != 15


class TestDekadHash:
    """Test hashing and use in collections."""

    def test_hash(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 15)
        assert hash(dekad1) == hash(dekad2)

    def test_hash_different_dekads(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 16)
        # Different dekads should have different hashes (usually)
        # Note: hash collisions are possible but unlikely
        assert hash(dekad1) != hash(dekad2)

    def test_use_in_set(self):
        dekad1 = Dekad(2024, 15)
        dekad2 = Dekad(2024, 15)
        dekad3 = Dekad(2024, 16)
        dekad_set = {dekad1, dekad2, dekad3}
        assert len(dekad_set) == 2

    def test_use_as_dict_key(self):
        dekad = Dekad(2024, 15)
        d = {dekad: 'value'}
        assert d[Dekad(2024, 15)] == 'value'


class TestDekadStringRepresentation:
    """Test string representations of Dekad objects."""

    def test_str(self):
        dekad = Dekad(2024, 15)
        assert str(dekad) == '2024-D15'

    def test_str_single_digit_dekad(self):
        dekad = Dekad(2024, 5)
        assert str(dekad) == '2024-D05'

    def test_repr(self):
        dekad = Dekad(2024, 15)
        assert repr(dekad) == 'Dekad(2024, 15)'

    def test_repr_eval(self):
        # repr should be evaluable
        dekad = Dekad(2024, 15)
        dekad_from_repr = eval(repr(dekad))
        assert dekad == dekad_from_repr


class TestDekadRange:
    """Test dekad_range utility function."""

    def test_basic_range(self):
        result = list(dekad_range(Dekad(2024, 1), Dekad(2024, 4)))
        expected = [Dekad(2024, 1), Dekad(2024, 2), Dekad(2024, 3)]
        assert result == expected

    def test_range_with_step_2(self):
        result = list(dekad_range(Dekad(2024, 1), Dekad(2024, 7), step=2))
        expected = [Dekad(2024, 1), Dekad(2024, 3), Dekad(2024, 5)]
        assert result == expected

    def test_range_negative_step(self):
        result = list(dekad_range(Dekad(2024, 5), Dekad(2024, 2), step=-1))
        expected = [Dekad(2024, 5), Dekad(2024, 4), Dekad(2024, 3)]
        assert result == expected

    def test_range_across_year_boundary(self):
        result = list(dekad_range(Dekad(2024, 35), Dekad(2025, 3)))
        expected = [
            Dekad(2024, 35),
            Dekad(2024, 36),
            Dekad(2025, 1),
            Dekad(2025, 2),
        ]
        assert result == expected

    def test_range_empty_when_start_equals_end(self):
        result = list(dekad_range(Dekad(2024, 5), Dekad(2024, 5)))
        assert result == []

    def test_range_empty_when_start_greater_than_end(self):
        result = list(dekad_range(Dekad(2024, 5), Dekad(2024, 3)))
        assert result == []

    def test_range_empty_negative_step_wrong_direction(self):
        result = list(dekad_range(Dekad(2024, 3), Dekad(2024, 5), step=-1))
        assert result == []

    def test_range_step_zero_raises_error(self):
        with pytest.raises(ValueError, match='Step cannot be zero'):
            list(dekad_range(Dekad(2024, 1), Dekad(2024, 5), step=0))

    def test_range_single_element(self):
        result = list(dekad_range(Dekad(2024, 5), Dekad(2024, 6)))
        expected = [Dekad(2024, 5)]
        assert result == expected


class TestDekadIntegration:
    """Integration tests for complex scenarios."""

    def test_full_year_iteration(self):
        # Iterate through all dekads in a year
        dekads = list(dekad_range(Dekad(2024, 1), Dekad(2025, 1)))
        assert len(dekads) == 36
        assert dekads[0] == Dekad(2024, 1)
        assert dekads[-1] == Dekad(2024, 36)

    def test_date_dekad_date_roundtrip(self):
        # Test that date -> dekad -> first_date is deterministic
        original_date = datetime.date(2024, 5, 15)
        dekad = Dekad.from_date(original_date)
        first_date = dekad.first_date()
        last_date = dekad.last_date()

        # Original date should be within the dekad range
        assert first_date <= original_date <= last_date
        # Converting the first date back should give the same dekad
        assert Dekad.from_date(first_date) == dekad
        # Converting the last date back should give the same dekad
        assert Dekad.from_date(last_date) == dekad

    def test_arithmetic_chain(self):
        # Test chaining arithmetic operations
        dekad = Dekad(2024, 15)
        result = dekad + 5 - 3 + 10
        assert result == Dekad(2024, 27)

    def test_sorting_dekads(self):
        # Test that dekads can be sorted
        dekads = [
            Dekad(2024, 15),
            Dekad(2023, 36),
            Dekad(2024, 5),
            Dekad(2025, 1),
        ]
        sorted_dekads = sorted(dekads)
        expected = [
            Dekad(2023, 36),
            Dekad(2024, 5),
            Dekad(2024, 15),
            Dekad(2025, 1),
        ]
        assert sorted_dekads == expected
