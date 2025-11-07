# cSpell: disable
import os
import sys
import inspect

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../src"))
from clig import clig  # protected functions


def test_normalize_docstring():
    def foo():
        """A multi-line
        docstring.
        """

    def bar():
        """
        A multi-line
        docstring.
        """

    def aba(a, b):
        """My function

        My sumary

        Parameters
        ----------
        a : str
            one string
        b : ing
            one int
        """

    def gue(a, b):
        """
        My function

        My sumary

        Parameters
        ----------
        a : str
            one string
        b : ing
            one int

        """

    assert clig._normalize_docstring(foo.__doc__) == clig._normalize_docstring(bar.__doc__)
    assert clig._normalize_docstring(aba.__doc__) == clig._normalize_docstring(gue.__doc__)


def test_normalize_docstring_with_inspect():
    def foo(a: int, b: str, c: float, d: bool = True, e: list[str] | None = None) -> None:
        """Fugit voluptatibus enim odit velit facilis.

        Neque dolores expedita repellat in perspiciatis dolorem aliquid et. Commodi fugit minima
        laudantium beatae et ut. Id possimus soluta magnam quisquam laboriosam impedit.

        Ad quaerat ut culpa aut iure id quia. Ut aut alias adipisci quia. Veritatis ratione
        dignissimos laborum. Molestiae molestias id earum.

        Nesciunt quas corrupti tenetur officiis occaecati asperiores eaque. Qui voluptas ut ea dolor
        et harum beatae quos. Est tenetur ut ipsum. Eveniet rem beatae error eum voluptatem tempora
        velit in. Ea doloribus similique.

        Parameters
        ----------
        - `a` (`int`):
            Quidem natus sunt molestiae et reprehenderit voluptas optio.

        - `b` (`str`):
            Unde rerum aut a et assumenda fugit dolorem eligendi corrupti.

        - `c` (`float`):
            Dolorum officiis totam aspernatur fuga voluptas similique.

        - `d` (`bool`, optional): Defaults to `True`.
            Ducimus sunt eum in vel voluptatibus aut facere perspiciatis.

        - `e` (`list[str] | None`, optional): Defaults to `None`.
            Sit et consequatur a asperiores sequi sint dolores id ipsam.

        Returns
        -------
        `tuple[str, ...]`:
            illo odit ut
        """
        pass
        assert foo.__doc__ is not None
        assert clig._normalize_docstring(foo.__doc__) == inspect.cleandoc(foo.__doc__)


def test_normalize_docstring_with_one_line():
    def one_line():
        """Test of one line in the docsting"""

    def one_line_with_lines():
        """
        Test of one line in the docsting
        """

    assert clig._normalize_docstring(one_line.__doc__) == clig._normalize_docstring(
        one_line_with_lines.__doc__
    )


def test_normalize_docstring_multiline():
    def foo():
        """
        Fuga nemo provident vero odio qui sint et aut veritatis. Facere necessitatibus ut. Voluptatem
        natus natus veritatis earum. Reprehenderit voluptate dolorem dolores consequuntur magnam impedit
        eius. Est ut nisi aut accusamus.
        """
        pass

    assert (
        clig._normalize_docstring(foo.__doc__)
        == """Fuga nemo provident vero odio qui sint et aut veritatis. Facere necessitatibus ut. Voluptatem
natus natus veritatis earum. Reprehenderit voluptate dolorem dolores consequuntur magnam impedit
eius. Est ut nisi aut accusamus."""
    )
