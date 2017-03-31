# Utils for the runnable tutorials on python
# Made by http://www.rakesh-chinta.github.io


def getLineSize(text):
    return max([len(x) for x in text.split('\n')])


def _print(text, sep, alsoAbove=False):
    size = getLineSize(text)

    print ''
    if alsoAbove:
        print sep * size
    print text.strip()
    print sep * size
    print ''


def printError(err):
    print str(err), type(err)
    print ''


def printTitle(text):
    _print(str.upper(text), '*', True)


def printSubTitle(text):
    _print(text.title(), '=')


def printExplain(text):
    _print(text, '-')


def printEqual(left, compare, rigth):
    print left, compare, rigth


def printTab(text):
    print '\t', text
