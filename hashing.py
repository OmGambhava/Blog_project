from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    def bcrypt(password):
        return pwd_context.hash(password)

    def verify(hased_password, plain_password):
        return pwd_context.verify(plain_password, hased_password)