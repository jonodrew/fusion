from typing import List, Dict, Any, Set, Union

from flask import json


class FastStreamer:
    """This class contains the methods and attributes of the FastStreamer object, which has a past history and future
    preferences. Future preferences should be considered alongside past experience. The class exists to store this
    data for manipulation in the munkres algorithm."""

    def __init__(self, identifier: int, skills: List[str]=None, anchors: List[str]=None, restrictions: List[str]=None,
                 clearance: str=None, departments: List[str]=None, national: bool=True,
                 location_restriction: bool=False) -> None:
        """

        @type anchors: List[str]
        @type identifier: int
        @param identifier:
        @param skills:
        @param anchors:
        @param restrictions:
        @param clearance:
        @param departments:
        @param national:
        @param location_restriction:
        """
        self.identifier = identifier
        self.clearance = clearance
        self.national = national
        self.location_restriction = location_restriction
        self.profile = {
            'skills': skills,
            'anchors': anchors,
            'restrictions': restrictions,
            'departments': departments
        }

        self.preferences = Preferences()

    def set_preferences(self, anchors: Dict[int, str], skills: List[str], dv: bool, po: bool, loc: List[str], sec: bool,
                        departments: Set[str]):
        """

        Args:
            anchors:
            skills:
            dv:
            po:
            loc:
            sec:
            departments:

        Returns:
            None

        """
        self.preferences = Preferences(anchors=anchors, skills=skills, undertake_dv=dv, want_po=po, locations=loc,
                                       secondment=sec, departments=departments)


class Post:
    def __init__(self, skills: List[str], anchor: str, clearance: str, location: str, department: str,
                 private_office: bool=False, identifier: int=0, reserved: bool=False):
        """
        This class contains information about the post, so it can be manipulated and matched
        Args:
            private_office (bool): Whether the Post is in a private office
            identifier (int): Unique identifier for the post
            skills(List[str]): List of skills the candidate will gain in the post
            anchor (str): The core capability built by the post
            clearance (str): The required clearance for this post
            location (str): The post's region
            department (str): The department or organisation where the post is
        """
        self.identifier = identifier
        self.department = department
        self.anchor = anchor
        self.skills = skills
        self.location = location
        self.clearance = clearance
        self.is_private_office = private_office
        self.reserved = reserved


class Match:
    weights_dict = {'anchor': 10, 'location': 2, 'skills': 5, 'department': 2}

    @staticmethod
    def check_if_equal(p_attribute: str, fs_attribute: str) -> int:
        """
        Compare two attributes. If they're equal, return True, otherwise return False.
        Args:
            p_attribute (str): some attribute of the post
            fs_attribute (str): some attribute of the FastStreamer

        Returns:
            int: the value of the match of the two attributes

        """
        return p_attribute == fs_attribute

    @staticmethod
    def create_match_score(scores: Dict[str, int]) -> int:
        """
        This method returns the sum of all the scores, passed as a dictionary
        Args:
            scores:

        Returns:

        """
        return sum([scores[k] for k in scores])

    @staticmethod
    def check_x_in_y_list(list_to_check: List[Any], value_to_check) -> bool:
        try:
            r = value_to_check in set(list_to_check)
        except TypeError:
            r = True
        return r

    @staticmethod
    def check_x_in_y_dict(dict_to_check: Dict[Any, Any], value_to_check) -> bool:
        return value_to_check in [v for k, v in dict_to_check.items()]

    @staticmethod
    def convert_clearances(clearance: str) -> int:
        """
        This function converts a clearance level as a string to an int for comparison
        Args:
            clearance: string representing clearance level

        Returns:
            int

        """
        c = {'SC': 3, 'DV': 4, 'CTC': 2, 'BPSS': 1}
        return c[clearance]

    @staticmethod
    def boolean_implication(a: bool, b: bool) -> bool:
        return (not a) or b

    @staticmethod
    def check_any_item_from_list_a_in_list_b(a: Union[List[str], Set], b: List) -> bool:
        return bool(set(a).intersection(set(b)))

    def suitable_location_check(self) -> bool:
        """
        Checks if FS has location restriction: if so, returns True if it's the location the FS wants, if not, returns
        False
        @return: bool
       """
        return (not self.fast_streamer.location_restriction) or self.check_x_in_y_list(
                self.fast_streamer.preferences.locations, self.post.location)

    def __init__(self, identifier, post_object: Post=None, fser_object: FastStreamer=None) -> None:
        self.identifier = identifier
        self.post = post_object
        self.fast_streamer = fser_object
        self.po_match = self.boolean_implication(self.post.is_private_office,
                                                 self.fast_streamer.preferences.wants_private_office)
        self.reserved_match = self.boolean_implication(self.post.reserved, self.fast_streamer.national)
        self.clearance_match = self.compare_clearance()
        self.suitable_location = self.suitable_location_check()
        if not(self.clearance_match and self.po_match and self.reserved_match and self.suitable_location):
            self.total = 0
            self.weighted_scores = {'anchor': 0, 'location': 0, 'skills': 0, 'department': 0}
            # this approach massively improves speed when generating the matrix, but also means that the match cannot
            # later be examined for how good or bad it was
        else:
            self.anchor_match = self.check_x_in_y_dict(self.fast_streamer.preferences.anchors, self.post.anchor)
            self.location_match = self.check_x_in_y_list(self.fast_streamer.preferences.locations, self.post.location)
            self.skills_match = self.check_any_item_from_list_a_in_list_b(self.post.skills,
                                                                          self.fast_streamer.preferences.skills)
            self.department_match = self.check_any_item_from_list_a_in_list_b(self.post.department,
                                                                              self.fast_streamer.preferences.departments)
            self.match_scores = {'anchor': self.anchor_match, 'location': self.location_match,
                                 'skills': self.skills_match, 'department': self.department_match}
            self.weighted_scores = self.apply_weighting(weighting_dict=Match.weights_dict)
            self.total = self.create_match_score(self.weighted_scores)

    def compare_clearance(self) -> bool:
        """
        Compares FastStreamer's clearance and Post clearance. Returns True if FastStreamer clearance is greater than
        or equal to Post clearance returns True, else returns False

        Returns:
            bool

        """
        post_c = self.convert_clearances(self.post.clearance)
        fs_c = self.convert_clearances(self.fast_streamer.clearance)
        if self.post.clearance == 'DV' and self.fast_streamer.preferences.will_undertake_dv is True:
            r = True
        else:
            r = post_c <= fs_c
        return r

    def compare_private_office(self) -> bool:
        return (not self.post.is_private_office) or self.fast_streamer.preferences.wants_private_office

    def apply_weighting(self, weighting_dict: Dict[str, int]) -> Dict[str, int]:
        return {k: self.match_scores[k] * weighting_dict[k] for k in self.match_scores}