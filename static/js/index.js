class MenuMobile {
    constructor() {
        this.menuButton = $('#menuMobile');
        this.menuStatus = false;

        this.initialBehavior();
    }

    initialBehavior() {
        this.menuButton.click(() => {
            this.toggleMenu();
        });
    }

    toggleMenu() {
        if (this.menuStatus) {
            $('#menuOptions').toggleClass('menu-mobile-active');
            this.menuButton.css({'transform': 'rotate(0deg)'});
            this.menuStatus = false;
        } else {
            $('#menuOptions').toggleClass('menu-mobile-active');
            this.menuButton.css({'transform': 'rotate(180deg)'});
            this.menuStatus = true;
        }
    }
}

class Modals {
    constructor() {
        this.initialBehavior();
    }

    initialBehavior() {
        this.newOptions = {
            "headOptionManga": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "headOptionAbout": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "headOptionContact": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "footOptionPrivacy": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "footOptionTerms": [
                "Still in development",
                "Sorry, but you'll have to wait for the next update."
            ],
            "footOptionAbout": [
                "Website in development",
                "By: <br> <a class='icon icon-github' href='https://github.com/grigio888'>Vinicius Grigio</a><a class='icon icon-github' href='https://github.com/phzsantos'>Paulo Henrique</a>"
            ],
        }

        Object.keys(this.newOptions).forEach(key => {
            $(`#${key}`).click(() => {
                this.enteringModal(`${key}Modal`, this.newOptions[key][0], this.newOptions[key][1]);

                // closing modal
                $(`.modal-close`).click(() => {
                    this.exitingModal(`.modal-background`);
                });
            });
        });
    }

    enteringModal(id, title, content) {
        $('<div>').addClass('modal-background').appendTo('body');
        $('<div>').addClass('modal').attr('id', id).appendTo('.modal-background');
        $('<div>').addClass('modal-content').appendTo('.modal');
        $('<span></span>').addClass('icon').addClass('modal-close').appendTo('.modal');

        $('<div>').addClass('modal-header').appendTo('.modal-content');
        $(`<h2>${title}</h2>`).appendTo('.modal-header');

        $('<div>').addClass('modal-body').appendTo('.modal-content');
        $(`<p>${content}</p>`).appendTo('.modal-body');

        $('.modal-background').css({'opacity': 0});
        $('.modal-background').animate({
            opacity: 1
        }, 250);
    }

    exitingModal(tag) {
        $(tag).animate({
            opacity: 0
        }, 250, () => {
            $(`${tag}`).remove();
        });
    }
}

class SearchBar {
    constructor() {
        this.searchInput = $('#searchInput');
        this.searchButton = $('#searchButton');

        this.initialBehavior();
    }

    initialBehavior() {
        this.searchButton.click((e) => {
            this.search(e);
        });
    }

    search(e) {
        e.preventDefault();

        if (this.searchInput.val().length > 0) {
            window.location.href = `/search/all/${this.searchInput.val()}`;
        } else {
            modals.enteringModal(`searchModal`, 'Oops', 'Looks like you forgot to type something.');

            // closing modal
            $(`.modal-close`).click(() => {
                modals.exitingModal(`.modal-background`);
            });
        }
    }
}


let menuMobile = new MenuMobile();
let modals = new Modals();
let searchBar = new SearchBar();