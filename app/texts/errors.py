from app.texts import Buttons


class Errors:
    PLACE_SELECT = "Sorry, I couldn't get the weather data for this place. Please try again later."
    PLACE_NAME_INVALID = ("To continue, please, enter the name of a Place or select it from the menu. "
                          "Or press Back ↩️ button below to go back.")
    PLACE_NAME_NO_EXIST = "⚠️ Such a place name doesn't exist. Please enter the correct one."
    PLACE_NAME_EMPTY = f"Please enter a correct Place name or press {Buttons.CANCEL} button."
    PLACE_LIST = "Sorry, I couldn't get the list of your places. Please try again later."
    PLACE_UPDATE = "Sorry, I couldn't update your place. Please try again later."
    PLACE_DELETE = "Sorry, I couldn't delete the place. Please try again later."
    PLACE_CREATE = "Sorry, I couldn't create a place. Please try again later."
    PLACE_ALREADY_EXIST = "⚠️ Place with this name already exists. Please enter different name."
    ACCOUNT_CREATE = "Sorry, I couldn't create an account. Please try again later."
    ACCOUNT_DELETE = "Sorry, I couldn't delete the account. Please try again later."
