@echo off
echo Python�̉��z�����N�����Ă��܂�...

REM ���z�������݂��邩�m�F
if not exist venv (
    echo ���z�������݂��܂���B�쐬���܂��B
    python -m venv venv
    echo ���z�����쐬���܂����B
    call venv\Scripts\activate
    echo ���z�����L���ɂȂ�܂����B
    python -m pip install --upgrade pip
    echo pip���A�b�v�f�[�g���܂����B
    pip install -r requirements.txt
    echo �K�v�ȃ��C�u�������C���X�g�[�����܂����B
) else (
    echo ���z�������݂��܂��B
    call venv\Scripts\activate
    echo ���z�����L���ɂȂ�܂����B
)

echo ���z�����L���ɂȂ�܂����B
echo �I������ɂ� "deactivate" �Ɠ��͂��Ă��������B

echo ================================================
echo >python manage.py migrate
echo >python manage.py runserver
echo http://127.0.0.1:8000/files/master/
echo ================================================

REM �R�}���h�v�����v�g���ێ�
cmd /k
