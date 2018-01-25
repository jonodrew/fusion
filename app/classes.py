from typing import List, Dict, Any


class FastStreamer:
    """This class contains the methods and attributes of the FastStreamer object, which has a past history and future
    preferences. Future preferences should be considered alongside past experience. The class exists to store this
    data for manipulation in the munkres algorithm."""

    def __init__(self, identifier: int, skills: List[str]=None, anchors: List[str]=None, restrictions: List[str]=None,
                 clearance: str=None, departments: List[str]=None) -> None:
        """

        Args:
            departments (List[str]): Departments the FastStreamer has previously been in
            identifier (int): The FastStreamer's unique id.
            skills (List[str]): The FastStreamer's previous skills.
            anchors (List[str]): The FastStreamer's previous anchors.
            restrictions: FastStreamers may have location restrictions due to caring responsibilities
            clearance (str) : Level of clearance will impact available roles
        """
        self.identifier = identifier
        self.clearance = clearance
        self.profile = {
            'skills': skills,
            'anchors': anchors,
            'restrictions': restrictions,
            'departments': departments
        }

        self.preferences = Preferences()

    def set_preferences(self, anchors: Dict[int, str], skills: List[str], dv: bool, po: bool, loc: str, sec: bool):
        """

        Args:
            anchors:
            skills:
            dv:
            po:
            loc:
            sec:

        Returns:
            None

        """
        self.preferences = Preferences(anchors=anchors, skills=skills, undertake_dv=dv, want_po=po, location=loc,
                                       secondment=sec)


class Post:
    def __init__(self, skills: List[str], anchor: str, clearance: str, location: str, department: str,
                 private_office: bool=False, identifier: int=0):
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


class Match:
    weights_dict = {'anchor': 10, 'location': 2}

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

    def __init__(self, identifier, post_object: Post=None, fser_object: FastStreamer=None) -> None:
        self.identifier = identifier
        self.post = post_object
        self.fast_streamer = fser_object
        self.po_match = self.compare_private_office()
        self.anchor_match = self.check_x_in_y_dict(self.fast_streamer.preferences.anchors, self.post.anchor)
        self.clearance_match = self.compare_clearance()
        self.location_match = self.check_if_equal(self.post.location, self.fast_streamer.preferences.location)
        self.match_scores = {'anchor': self.anchor_match, 'location': self.location_match}
        self.weighted_scores = self.apply_weighting(weighting_dict=Match.weights_dict)
        self.total = self.create_match_score(self.weighted_scores)
        # if the FastStreamer doesn't have clearance, this will destroy the match. Desired behaviour?
        self.total *= self.compare_clearance() * self.po_match

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

    @staticmethod
    def check_x_in_y_list(list_to_check: List[Any], value_to_check) -> bool:
        return value_to_check in set(list_to_check)

    @staticmethod
    def check_x_in_y_dict(dict_to_check: Dict[Any, Any], value_to_check) -> bool:
        return value_to_check in [v for k, v in dict_to_check.items()]

    def apply_weighting(self, weighting_dict: Dict[str, int]) -> Dict[str, int]:
        return {k: self.match_scores[k] * weighting_dict[k] for k in self.match_scores}


class Preferences:
    def __init__(self, anchors: Dict[int, str]=None, skills=None, undertake_dv=False, want_po=False, location=None,
                 secondment=False):
        if anchors is None:
            self.anchors = {1: "", 2: ""}
        else:
            self.anchors = anchors
        self.skills = skills
        self.will_undertake_dv = undertake_dv
        self.wants_private_office = want_po
        self.location = location
        self.secondment = secondment
