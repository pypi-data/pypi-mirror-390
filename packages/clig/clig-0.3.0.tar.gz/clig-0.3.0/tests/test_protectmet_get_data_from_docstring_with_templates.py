# cSpell: disable
import sys
from pathlib import Path

this_dir = Path(__file__).parent

sys.path.insert(0, str((this_dir).resolve()))
sys.path.insert(0, str((this_dir / "../src").resolve()))
from clig import clig  # protected functions
import functions as fun


def adjust_epilog_for_test(text: str) -> str:
    """First and last lines must be always empty"""
    return "\n".join([line.strip() for line in text.splitlines()[1:-1]])


def test_inferdoctemplate__descr():
    cmd = clig.Command(fun.descr, docstring_template=clig.DESCRIPTION_DOCSTRING)
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "A foo that bars"


def test_inferdoctemplate__descrEpilog_fromFun():
    cmd = clig.Command(fun.descrEpilog, docstring_template=clig.DESCRIPTION_DOCSTRING)
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == clig._normalize_docstring(fun.descrEpilog.__doc__)


def test_inferdoctemplate__descrEpilog():
    epilog = adjust_epilog_for_test(
        """
        Corporis ullam nam ut dolores sed. Nemo ea deserunt facere numquam velit aut. Architecto provident
        consequatur ratione est quas qui dolor ratione. Laudantium fugit at.

        Ullam et temporibus eum. Sit voluptatem tempora totam dolores. Pariatur accusamus voluptate totam.
        Fugit rerum nemo reiciendis veritatis modi sit distinctio ratione id.

        Voluptates tenetur quos qui exercitationem laudantium aliquid. Neque qui eum qui. Qui tenetur facilis
        non voluptatem ut corporis harum fugiat.
        """
    )
    cmd = clig.Command(fun.descrEpilog, docstring_template=clig.DESCRIPTION_EPILOG_DOCSTRING)
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Aliquam alias quia earum."
    assert data.epilog == epilog


def test_inferdoctemplate__pti_ptc_ptf_ktb_ktlo_numpyEpilog():
    epilog = adjust_epilog_for_test(
        """
        Blanditiis velit consequatur omnis odit magnam quo dignissimos. Qui ex et illo. Et
        necessitatibus ea placeat consectetur itaque dolore fugiat quo autem. Ut accusamus incidunt
        repellat minima est soluta ut est. Id aut enim ad. Quia qui sint ex eos eveniet eveniet
        earum unde.

        Non rerum aut consectetur ut ducimus ut similique ut illum. Aut qui et distinctio. Nihil id
        sit incidunt minus omnis. Quo unde inventore fuga. Quasi ea ea dolores quam.

        Esse temporibus voluptas nulla. Odio voluptas nisi quae cupiditate consequatur cumque ut ex
        dolorem. Est doloremque quis nostrum voluptates doloremque quia. Ex sunt dolores consectetur
        veritatis maxime suscipit. Fugit dolorem facilis quasi.
        """
    )

    cmd = clig.Command(
        fun.pti_ptc_ptf_ktb_ktlo_numpyEpilog,
        docstring_template=clig.NUMPY_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Distinctio et ratione sequi hic."
    assert data.epilog == epilog
    assert all([p in d for p, d in zip(["a", "b", "c", "d", "e"], data.helps.keys())])
    assert data.helps["a"] == "Neque ut qui non nulla odit esse accusantium aut suscipit."
    assert data.helps["b"] == "Nihil dolores autem autem nulla sit nihil molestiae vero est."
    assert data.helps["c"] == "Animi magnam ut sapiente maiores."
    assert data.helps["d"] == "Consequatur provident neque optio consequatur., by default True"
    assert data.helps["e"] == "Corrupti molestiae in aspernatur., by default None"


def test_inferdoctemplate__pti_ptc_ptf_ktb_ktlo_sphinxEpilog():
    epilog = adjust_epilog_for_test(
        """
        Est nam quia voluptatem vero architecto laborum. Accusantium delectus et aut repudiandae
        voluptatibus qui iure ut debitis. Voluptatibus ut enim consequatur iusto eaque dolor.
        """
    )
    cmd = clig.Command(
        fun.pti_ptc_ptf_ktb_ktlo_sphinxEpilog,
        docstring_template=clig.SPHINX_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Qui accusantium harum debitis et."
    assert data.epilog == epilog
    assert data.helps["a"] == "Atque pariatur excepturi sed dolorem sint impedit molestiae."
    assert data.helps["b"] == "magni optio voluptatibus"
    assert data.helps["c"] == "Sit eligendi consequatur recusandae doloribus enim amet."
    assert data.helps["d"] == "Soluta dolorum amet et., defaults to True"
    assert data.helps["e"] == "Fugiat provident amet iste natus ab voluptas., defaults to None"


def test_inferdoctemplate__pti_ptc_ptf_ktb_ktlo_googleEpilog():
    epilog = adjust_epilog_for_test(
        """
        Maiores occaecati quam asperiores non sunt est dolor laborum est. Eius corporis nobis
        accusamus rerum et et et. Ducimus tempore voluptas qui aut consectetur saepe quos cum
        delectus. Tempora adipisci odit qui. Optio eum magni non. Placeat repudiandae quasi nostrum
        mollitia sunt neque fuga id possimus.
        """
    )
    cmd = clig.Command(
        fun.pti_ptc_ptf_ktb_ktlo_googleEpilog,
        docstring_template=clig.GOOGLE_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Voluptatum dolorem quis dolorum voluptas atque non temporibus."
    assert data.epilog == epilog
    assert data.helps["a"] == "Qui eum eius nihil voluptas quia aut numquam."
    assert data.helps["b"] == "Quasi voluptates dicta cumque similique qui dolorem architecto."
    assert data.helps["c"] == "Sint harum et omnis nobis numquam quos omnis."
    assert data.helps["d"] == "Ex voluptas animi.. Defaults to True."
    assert data.helps["e"] == "In vero ut nisi officia ut.. Defaults to None."


def test_inferdoctemplate__pti_ptc_ptf_ktb_ktlo_cligEpilog():
    clig_example_epilog = adjust_epilog_for_test(
        """
        Neque dolores expedita repellat in perspiciatis dolorem aliquid et. Commodi fugit minima
        laudantium beatae et ut. Id possimus soluta magnam quisquam laboriosam impedit.

        Ad quaerat ut culpa aut iure id quia. Ut aut alias adipisci quia. Veritatis ratione
        dignissimos laborum. Molestiae molestias id earum.

        Nesciunt quas corrupti tenetur officiis occaecati asperiores eaque. Qui voluptas ut ea dolor
        et harum beatae quos. Est tenetur ut ipsum. Eveniet rem beatae error eum voluptatem tempora
        velit in. Ea doloribus similique.
        """
    )
    cmd = clig.Command(
        fun.pti_ptc_ptf_ktb_ktlo_cligEpilog,
        docstring_template=clig.CLIG_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Fugit voluptatibus enim odit velit facilis."
    assert data.epilog == clig_example_epilog
    assert data.helps["a"] == "Quidem natus sunt molestiae et reprehenderit voluptas optio."
    assert data.helps["b"] == "Unde rerum aut a et assumenda fugit dolorem eligendi corrupti."
    assert data.helps["c"] == "Dolorum officiis totam aspernatur fuga voluptas similique."
    assert data.helps["d"] == "Ducimus sunt eum in vel voluptatibus aut facere perspiciatis."
    assert data.helps["e"] == "Sit et consequatur a asperiores sequi sint dolores id ipsam."


def test_inferdoctemplate__pti_ptc_ptf_ktb_ktlo_numpyEpilogMultiline():
    epilog = adjust_epilog_for_test(
        """
        Qui deserunt sequi aut illo. Minima modi illo sit occaecati. Ducimus illum et. Deleniti repellendus
        cum quasi ut et natus dolorem. Aliquam aut aperiam qui.

        Sint maiores dolorum. Nobis quo distinctio consequuntur. Recusandae fuga qui perspiciatis quisquam.
        Nostrum asperiores neque nisi. Enim voluptatem eum illo.

        Est labore illum voluptatibus at ut. Deleniti ut aut ut aperiam consequatur aut. Reprehenderit
        voluptatem est voluptates temporibus et voluptate accusamus dolores. Placeat nihil dignissimos sed
        sequi sequi.
        """
    )
    cmd = clig.Command(
        fun.pti_ptc_ptf_ktb_ktlo_numpyEpilogMultiline,
        docstring_template=clig.NUMPY_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Voluptatibus eos ipsa ex debitis voluptatem dignissimos."
    assert data.epilog == epilog
    assert data.helps["a"] == clig._normalize_docstring(
        """Fuga nemo provident vero odio qui sint et aut veritatis. Facere necessitatibus ut. Voluptatem
        natus natus veritatis earum. Reprehenderit voluptate dolorem dolores consequuntur magnam impedit
        eius. Est ut nisi aut accusamus."""
    )
    assert (
        data.helps["b"] == """Culpa asperiores incidunt molestias aliquam soluta voluptas excepturi nulla."""
    )
    assert data.helps["c"] == clig._normalize_docstring(
        """Non vitae qui non magni harum eum maiores qui. Dicta sunt voluptatem voluptate. At quibusdam
        aliquam autem et perspiciatis et assumenda. Perferendis qui velit quam numquam iste."""
    )
    assert data.helps["d"] == clig._normalize_docstring(
        """Aut ipsam aut velit impedit. Quidem expedita aliquid sed officia in ex et. Nihil rem adipisci ut
        perferendis iure., by default True"""
    )
    assert data.helps["e"] == clig._normalize_docstring(
        """Ratione consequatur molestiae quia deserunt quo. Non cupiditate sunt commodi vero labore
        doloremque voluptatem officiis est. Iusto voluptate reiciendis iusto in. Occaecati quia soluta
        minus perspiciatis alias illum iste aperiam et. Autem accusamus unde omnis est cum ducimus. Iure
        adipisci id omnis quis placeat impedit rerum ab aspernatur.

        Praesentium id rerum quod provident odit dolores adipisci veniam natus. Porro repellat aliquid
        quibusdam recusandae hic voluptas accusantium voluptatem voluptatem. Laboriosam similique nobis
        aut iusto et ab minima cum.

        Voluptas molestiae mollitia autem distinctio magnam dolorem molestiae aliquid. Neque provident
        impedit et. Quod quibusdam nulla cupiditate. Praesentium neque vel ea velit consequatur quis
        voluptate iste. Quae veniam sequi et nihil qui vel voluptatem maxime. Laborum corrupti dolores
        voluptate placeat fugit non nobis., by default None"""
    )


def test_inferdoctemplate__pti_ptc_ptf_ktb_ktlo_sphinxEpilogMultiline():
    epilog = adjust_epilog_for_test(
        """
        Quia aspernatur doloribus id doloribus sunt ratione et voluptatum. Eligendi numquam sed. Voluptas
        consequuntur quibusdam debitis quia unde doloribus ducimus sunt. Et provident assumenda hic eum sint
        quia ipsum sit sed.
        """
    )
    cmd = clig.Command(
        fun.pti_ptc_ptf_ktb_ktlo_sphinxEpilogMultiline,
        docstring_template=clig.SPHINX_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Est sit minus quasi soluta unde vero deleniti eligendi."
    assert data.epilog == epilog
    assert data.helps["a"] == """Velit ratione harum in quia laborum ut est quis."""
    assert data.helps["b"] == clig._normalize_docstring(
        """Adipisci voluptates aut fugiat qui nam non. Eveniet molestiae voluptas explicabo fuga.
        Beatae ex sed nostrum incidunt."""
    )
    assert data.helps["c"] == clig._normalize_docstring(
        """Non non voluptatum ipsum sit maiores et eum adipisci. Autem sit possimus et similique atque.
        Nihil tempore et excepturi.

        Nisi magnam et. Illum minus ea enim eligendi doloremque consequatur odit est officiis. Dolorem
        dolores repellat esse vero quae. Laboriosam ab qui quo eveniet quia ex et. Aut facilis molestias
        qui. Dolorum sit magni repellat iusto aut vel.

        Laborum dolores illum modi. Id et qui nisi harum aperiam doloribus. Quod quibusdam dolorum iusto."""
    )
    assert data.helps["d"] == clig._normalize_docstring(
        """Et magni harum adipisci accusantium aut et ipsum impedit. Sit modi voluptatem. Esse quis aut
        ex. Dicta quam rem repellendus accusantium aut molestias praesentium fugiat corporis. Assumenda
        eum natus voluptatem alias dolorem vitae dolor repudiandae inventore. Et deleniti repellendus
        quo., defaults to True"""
    )
    assert data.helps["e"] == clig._normalize_docstring(
        """Corporis est rerum. Aspernatur dolor porro a culpa omnis. Repudiandae totam necessitatibus
        quibusdam ipsum numquam eveniet dolor quasi. Dolores dolorem voluptate aut. Deleniti officia qui
        molestiae. Quo deserunt nulla aut sit sunt quam nostrum odit et., defaults to None"""
    )


def test_inferdoctemplate__pti_ptc_ptf_ktb_ktlo_googleEpilogMultiline():
    epilog = adjust_epilog_for_test(
        """
        Et perferendis quia et sit maxime. Accusantium vel sint quam perspiciatis minus explicabo. Incidunt
        iste error autem impedit deserunt tempore quo aut odit.
        """
    )
    cmd = clig.Command(
        fun.pti_ptc_ptf_ktb_ktlo_googleEpilogMultiline,
        docstring_template=clig.GOOGLE_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "nesciunt beatae asperiores"
    assert data.epilog == epilog
    assert data.helps["a"] == clig._normalize_docstring(
        """Vel similique placeat. Nam enim perspiciatis qui earum voluptas quis. Perspiciatis ut
        vitae. Aspernatur ab ratione libero ex hic consequatur. Nam cupiditate earum. Nihil ea
        exercitationem ut."""
    )
    assert data.helps["b"] == clig._normalize_docstring(
        """Molestiae velit et expedita autem quam. Omnis dolorem placeat est. Quidem illum eveniet
        enim exercitationem aut qui dolore est et. Rerum est iste laudantium qui praesentium et. Et
        deserunt voluptates harum voluptas voluptates iste saepe consequatur."""
    )
    assert data.helps["c"] == clig._normalize_docstring(
        """Quae minima eligendi veniam aperiam libero temporibus quia qui atque. Velit ea aut vel
        quibusdam commodi id laboriosam inventore aliquam. Nam nisi itaque et sed dolor praesentium
        molestiae quisquam cupiditate. Voluptatem mollitia dolorem est deleniti repellat cum
        voluptatem voluptas sit.

        Sit animi dolore neque libero voluptatibus. Illum voluptatum ullam distinctio quisquam sequi
        delectus quia similique sit. Id enim vel eius iure rerum veritatis eos rem et. Nemo est
        assumenda aut et quo. Et soluta corrupti amet perferendis maxime.

        Placeat aut consequatur vel quo impedit doloribus et in libero. Voluptas ducimus suscipit.
        Assumenda alias est sed asperiores similique id consequuntur. Voluptas rerum placeat
        perferendis possimus ratione at. Ea ut aut id explicabo voluptas."""
    )
    assert data.helps["d"] == clig._normalize_docstring(
        """Error ut architecto fugit natus qui tempora vitae. A sed sequi reprehenderit
        quia autem voluptatem enim. Numquam cum minus cum eos est. Illo voluptas ducimus minus ipsam
        quae dolores quam quo. Quod qui sed incidunt rerum sed. Incidunt repellendus est est labore
        laudantium quia voluptas ipsum.. Defaults to True."""
    )
    assert data.helps["e"] == clig._normalize_docstring(
        """Explicabo tenetur beatae consequuntur atque aut omnis et. Eveniet
        ipsum repellat voluptatibus sit.

        Placeat eum veritatis praesentium voluptates quia beatae
        repellendus suscipit. Sint neque deserunt quis. Incidunt quibusdam voluptatem animi voluptas
        in. Voluptas dolor aut quisquam.. Defaults to None."""
    )


def test_inferdoctemplate__ptc_kti_ktb_cligDocMutiline():
    epilog = adjust_epilog_for_test(
        """
        Qui quidem quo eligendi officia ea quod ab tempore esse. Sapiente quasi est sint. Molestias et
        laudantium quidem laudantium animi voluptate asperiores illum. Adipisci tempora nesciunt dolores
        tempore consequatur amet. Aut ipsa ex.
        """
    )
    cmd = clig.Command(
        fun.ptc_kti_ktb_cligDocMutiline,
        docstring_template=clig.CLIG_DOCSTRING_WITH_EPILOG,
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Reprehenderit unde commodi doloremque rerum ducimus quam accusantium."
    assert data.epilog == epilog
    assert data.helps["a"] == "Dicta et optio dicta."
    assert data.helps["b"] == "Dolorum voluptate voluptas nisi."
    assert data.helps["c"] == clig._normalize_docstring(
        """Asperiores quisquam odit voluptates et eos incidunt. Maiores minima provident doloremque aut
        dolorem. Minus natus ab voluptatum totam in. Natus consectetur modi similique rerum excepturi
        delectus aut."""
    )


def test_docstringdata__pn_pn_knb_kni_numpyEpilogNoType():
    cmd = clig.Command(
        fun.pn_pn_knb_kni_numpyEpilogNoType, docstring_template=clig.NUMPY_DOCSTRING_WITH_EPILOG_NOTYPES
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Odio est rerum iure porro rerum voluptatum libero magnam."
    assert data.epilog == "In vitae ut distinctio optio corrupti cumque rerum quasi aut."
    assert data.helps["a"] == "hic omnis sint"
    assert data.helps["b"] == "Ut rem quis delectus."
    assert data.helps["c"] == "Et tenetur modi ea., by default False"
    assert data.helps["d"] == "recusandae autem vero, by default 123"


def test_docstringdata__pn_pn_knb_kni_googleEpilogNoType():
    cmd = clig.Command(
        fun.pn_pn_knb_kni_googleEpilogNoType, docstring_template=clig.GOOGLE_DOCSTRING_WITH_EPILOG_NOTYPES
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Odio est rerum iure porro rerum voluptatum libero magnam."
    assert data.epilog == "In vitae ut distinctio optio corrupti cumque rerum quasi aut."
    assert data.helps["a"] == "Quasi veniam facere et."
    assert data.helps["b"] == clig._normalize_docstring(
        """Quis ex modi vel sed ea dolorum magnam. Ut veniam veniam minus. Laboriosam voluptatem quod et. Et
            eaque sint quasi libero mollitia."""
    )
    assert data.helps["c"] == "architecto non voluptas. Defaults to False."
    assert (
        data.helps["d"]
        == "Omnis laboriosam aut saepe nobis consequatur nihil eos accusantium.. Defaults to 123."
    )


def test_docstringdata__pn_pn_knb_kni_sphinxEpilogNoType():
    cmd = clig.Command(
        fun.pn_pn_knb_kni_sphinxEpilogNoType, docstring_template=clig.SPHINX_DOCSTRING_WITH_EPILOG_NOTYPES
    )
    data = cmd._get_data_from_docstring()
    assert data is not None
    assert data.description == "Odio est rerum iure porro rerum voluptatum libero magnam."
    assert data.epilog == "In vitae ut distinctio optio corrupti cumque rerum quasi aut."
    assert data.helps["a"] == "aperiam enim voluptate"
    assert data.helps["b"] == "Totam voluptas porro est sint."
    assert data.helps["c"] == "Iusto impedit numquam ut., defaults to False"
    assert data.helps["d"] == "Corporis quis fugit eveniet rerum., defaults to 123"
