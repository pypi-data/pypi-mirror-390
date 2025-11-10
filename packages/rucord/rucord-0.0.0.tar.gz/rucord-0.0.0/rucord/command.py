from typing import Callable, Dict, Any, Awaitable


Table_For_Commands: Dict[str, "Command"] = {} 


class Command:
    def __init__(this, name: str, callback: Callable[..., Awaitable[Any]]):
        this.name = name
        this.callback = callback

    async def invoke(this, interaction):
        """Вызывается ботом при активации команды"""
        await this.callback(interaction)


def command(name: str) -> Callable:
    """Декоратор для создания команды

    Параметры
    ----------
    name: Optional[Union[:class:`str`, :class:`.Localized`]]
        The name of the slash command (defaults to function name).

    description: Optional[Union[:class:`str`, :class:`.Localized`]]
        The description of the slash command. It will be visible in Discord.

    nsfw: :class:`bool`
        Whether this command is :ddocs:`age-restricted <interactions/application-commands#agerestricted-commands>`.
        Defaults to ``False``.

    install_types: Optional[:class:`.ApplicationInstallTypes`]
        The installation types where the command is available.
        Defaults to :attr:`.ApplicationInstallTypes.guild` only.
        Only available for global commands.

        See :ref:`app_command_contexts` for details.

    contexts: Optional[:class:`.InteractionContextTypes`]
        The interaction contexts where the command can be used.
        Only available for global commands.

        See :ref:`app_command_contexts` for details.

    options: List[:class:`.Option`]
        The list of slash command options. The options will be visible in Discord.
        This is the old way of specifying options. Consider using :ref:`param_syntax` instead.

    dm_permission: :class:`bool`
        Whether this command can be used in DMs.
        Defaults to ``True``.

    default_member_permissions: Optional[Union[:class:`.Permissions`, :class:`int`]]
        The default required permissions for this command.
        See :attr:`.ApplicationCommand.default_member_permissions` for details.

    guild_ids: List[:class:`int`]
        If specified, the client will register the command in these guilds.
        Otherwise, this command will be registered globally.

    connectors: Dict[:class:`str`, :class:`str`]
        Binds function names to option names. If the name
        of an option already matches the corresponding function param,
        you don't have to specify the connectors. Connectors template:
        ``{"option-name": "param_name", ...}``.
        If you're using :ref:`param_syntax`, you don't need to specify this.

    extras: Dict[:class:`str`, Any]
        A dict of user provided extras to attach to the command.

        .. note::
            This object may be copied by the library.

    Возвращает
    -------
    Callable[..., :class:`InvokableSlashCommand`]
        A decorator that converts the provided method into an InvokableSlashCommand and returns it.
    """
    
    def getDecorator(function: Callable[..., Awaitable[Any]]):
        cmd = Command(name, function)
        Table_For_Commands[name] = cmd
        
        return function  # Возвращаем оригинальную функцию (удобно для тестов)
    
    return getDecorator