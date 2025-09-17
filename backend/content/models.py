from django.db import models


class MediaType(models.TextChoices):
    PHOTO = "PHOTO", "Фото"
    VIDEO = "VIDEO", "Видео"
    DOCUMENT = "DOCUMENT", "Документ"
    AUDIO = "AUDIO", "Аудио"
    MEDIA_GROUP = "MEDIA_GROUP", "Медиагруппа (несколько фото)"


class SiteSettings(models.Model):
    community_link = models.URLField(
        max_length=200,
        verbose_name="Ссылка на группу единомышленников",
        help_text="URL-адрес на группу единомышленников.",
        default="https://t.me/your_community_link",
    )

    def __str__(self):
        return "Группа единомашленников"

    class Meta:
        verbose_name = "Группа единомашленников"
        verbose_name_plural = "Группа единомашленников"


class FAQ(models.Model):
    question = models.CharField(
        max_length=255, verbose_name="Вопрос", help_text="Краткий текст вопроса."
    )
    answer = models.TextField(
        verbose_name="Ответ",
        help_text="Полный текст ответа.",
    )
    media_file = models.FileField(
        upload_to="faq_media/",
        blank=True,
        null=True,
        verbose_name="Медиафайл",
        help_text="Опциональный файл для отправки (фото, видео, документ, аудио).",
    )
    media_type = models.CharField(
        max_length=15,
        choices=MediaType.choices,
        blank=True,
        null=True,
        verbose_name="Тип медиафайла",
        help_text="Необходимо указать тип, если вы прикрепили медиафайл.",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Чем меньше число, тем выше в списке будет вопрос.",
    )

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["order", "question"]


class BotTexts(models.Model):
    welcome_message = models.TextField(
        verbose_name="Приветственное сообщение",
        default="Добро пожаловать в челлендж «400 продуктов»! Я помогу вам отслеживать ваш прогресс.",
        help_text="Отображается после успешной авторизации.",
    )
    request_contact_message = models.TextField(
        verbose_name="Запрос номера телефона",
        default="Здравствуйте! Для участия в челлендже, пожалуйста, поделитесь своим контактом.",
        help_text="Первое сообщение пользователю при команде /start, если он не авторизован.",
    )

    request_fio_message = models.TextField(
        verbose_name="Запрос ФИО",
        default="Отлично! Теперь, пожалуйста, введите ваше ФИО.",
        help_text="Сообщение с запросом ФИО пользователя.",
    )
    request_hw_message = models.TextField(
        verbose_name="Запрос роста и веса",
        default="Спасибо! И последний шаг: введите ваш рост (в см) и вес (в кг) через пробел.\n\nНапример: 180 75",
        help_text="Сообщение с запросом роста и веса.",
    )
    registration_success_message = models.TextField(
        verbose_name="Сообщение об успешной регистрации",
        default="Регистрация успешно завершена! Ваш челлендж начался.",
        help_text="Отображается после ввода всех данных.",
    )

    already_authorized_message = models.TextField(
        verbose_name="Сообщение для уже авторизованных",
        default="Вы уже авторизованы.",
        help_text="Когда пользователь с контактом пытается снова отправить контакт.",
    )

    main_menu_message = models.TextField(
        verbose_name="Сообщение главного меню",
        default="Вы в главном меню.",
        help_text="Текст, который видит пользователь в главном меню.",
    )
    menu_return_message = models.TextField(
        verbose_name="Сообщение о возврате в меню",
        default="Вы вернулись в главное меню.",
        help_text="Отображается при нажатии на кнопку 'Вернуться в меню'.",
    )

    faq_list_title = models.TextField(
        verbose_name="Заголовок списка FAQ",
        default="Часто задаваемые вопросы:",
        help_text="Текст, который отображается над списком вопросов в разделе FAQ.",
    )
    suggest_product_prompt = models.TextField(
        verbose_name="Запрос на предложение продукта",
        default="Если вы не увидели определенный продукт в нашем списке, то можете написать его сюда, мы рассмотрим и добавим его в ближайшее время.",
        help_text="Отображается при нажатии на кнопку 'Предложить продукт'.",
    )
    suggest_product_success = models.TextField(
        verbose_name="Успешное предложение продукта",
        default="Спасибо! Ваше предложение отправлено на рассмотрение.",
        help_text="Отображается после того, как был предложен продукт.",
    )

    def __str__(self):
        return "Тексты бота"

    class Meta:
        verbose_name = "Тексты бота"
        verbose_name_plural = "Тексты бота"


class AboutProject(models.Model):
    text = models.TextField(
        verbose_name="Текст 'О проекте'",
        help_text="Полный текст о челлендже.",
    )
    media_file = models.FileField(
        upload_to="about_media/",
        blank=True,
        null=True,
        verbose_name="Медиафайл",
    )
    media_type = models.CharField(
        max_length=15,
        choices=MediaType.choices,
        blank=True,
        null=True,
        verbose_name="Тип медиафайла",
        help_text="Выберите 'Медиагруппа' для загрузки нескольких фото ниже. В противном случае, загрузите один файл выше.",
    )

    def __str__(self):
        return "О проекте"

    class Meta:
        verbose_name = "О проекте"
        verbose_name_plural = "О проекте"


class AboutProjectMedia(models.Model):
    about_project = models.ForeignKey(
        AboutProject,
        on_delete=models.CASCADE,
        related_name="media_items",
        verbose_name="Связь с 'О проекте'",
    )
    image = models.ImageField(
        upload_to="about_media_group/",
        verbose_name="Фото",
        help_text="Фотография для медиагруппы.",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Чем меньше число, тем раньше будет фото в группе.",
    )

    def __str__(self):
        return f"Фото #{self.pk} для 'О проекте'"

    class Meta:
        verbose_name = "Медиа для 'О проекте'"
        verbose_name_plural = "Медиа для 'О проекте'"
        ordering = ["order"]
