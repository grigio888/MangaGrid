class Header {
    constructor() {
        this.menuButton = $('#menuMobile');
        this.menuStatus = false;

        this.initialBehavior();
    }

    initialBehavior() {
        this.verifySession();

        $('#headToggleTheme').click(() => {
            this.changeTheme();
        });
    }

    async checkingCurrentTheme () {
        let theme = await tools.asyncFetch('GET','/api/users/session/theme');

        if (theme.status == 200) {
            if (theme.data.theme == 'dark') {
                $('#headToggleTheme').find('div').removeClass('icon-light-theme').addClass('icon-dark-theme');
                $('#headToggleTheme').find('a').text('Dark');
            } else {
                $('#headToggleTheme').find('div').removeClass('icon-dark-theme').addClass('icon-light-theme');
                $('#headToggleTheme').find('a').text('Light')
            }
        }
    }

    async verifySession() {
        let verifySession = await tools.asyncFetch('GET','/api/users/session/is_alive');

        if (verifySession.status == 200) {
            this.settingPreferences();
        } else {
            $('#profileName').text('Login');
            $('#headOptionFavorites').remove();
            $('#headOptionHistory').remove();

            if (verifySession.data.cookies_acpted == false) {
                modals.enteringModalBottom('This site use cookies in order to improve your experience. By clicking "Accept" you accept the use of cookies.', 'Accept');
                $('.modal-bottom').find('button').click(() => {
                    tools.asyncFetch('POST','/api/users/session/cookies_accepted');
                });
            }
        }

        this.checkingCurrentTheme();
    }

    async changeTheme() {
        await tools.asyncFetch('POST','/api/users/session/theme');
        
        let theme = await tools.asyncFetch('GET','/api/users/session/theme');
        if (theme.status == 200) {
            $('html').attr('data-theme', theme.data.theme);
        }

        this.checkingCurrentTheme();
    }

    async settingPreferences() {
        let preferences = await tools.asyncFetch('GET','/api/users/session/get_profile');

        if (preferences.status == 200) {
            $('#profileName').text(preferences.data.user_username);
            $('.icon-logo').attr('href', preferences.data.user_main_page);
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
                "By: <br> <a class='icon icon-github' href='https://github.com/grigio888'>Vinicius Grigio</a>"//"<a class='icon icon-github' href='https://github.com/phzsantos'>Paulo Henrique</a>"
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
        
        $('<span></span>').addClass('icon').addClass('modal-close').appendTo('.modal');
        $('<div>').addClass('modal-content').appendTo('.modal');

        $('<div>').addClass('modal-header').appendTo('.modal-content');
        $(`<h2>${title}</h2>`).appendTo('.modal-header');

        $('<div>').addClass('modal-body').appendTo('.modal-content');
        $(`<p>${content}</p>`).appendTo('.modal-body');

        $('.modal-background').css({'opacity': 0});
        $('.modal-background').animate({
            opacity: 1
        }, tools.timeTransition);
    }

    enteringModalBottom(content, button) {
        $('<div>').addClass('modal-bottom').appendTo('body');

        $(`<p>${content}</p>`).addClass('modal-bottom-content').appendTo('.modal-bottom');
        $(`<button class='primary-button'>${button}</button>`).addClass('modal-bottom-button').appendTo('.modal-bottom');

        $('.modal-bottom').animate({
            'max-height': '100%'
        }, tools.timeTransition);

        $('.modal-bottom .primary-button').click(() => {
            this.exitingModal('.modal-bottom');
        });
    }

    exitingModal(tag) {
        $(tag).animate({
            opacity: 0
        }, tools.timeTransition, () => {
            $(`${tag}`).remove();
        });
    }

    errorMsg (msg, redirect = true) {
        this.enteringModal(
            `errorModal`,
            'Error',
            `Looks like we entered on a dead end.<br>I'll send you back.<br><br>${msg}`
        );
        if (redirect) {
            setTimeout(() => {
                window.location.href = `/`;
            }, tools.timeError);
        }
    }

    alertMsg(head, msg) {
        this.enteringModal(
            `alertModal`,
            `${head}`,
            `${msg}`
        );
        $(`.modal-close`).click(() => {
            this.exitingModal(`.modal-background`);
        }); 
    }

    loadingMsg (msg) {
        this.enteringModal(
            `loadingModal`,
            'Loading',
            `Please wait while we are loading.`
        );
        $('.modal-close').remove();
        $('<div>').addClass('loading-icon').appendTo('.modal-body');
    }

    confirmPasswordMsg (callback, section) {
        this.enteringModal(
            `confimModal`,
            'Confirmation',
            `Please, confirm your password:<br><br><br>
            <div class="form-row" id="passwordRow">
                <label for="password">Password</label>
                <input type="password" id="password" name="password">
            </div><br><br>
            <div class="form-row" id="passwordConfirmRow">
                <label for="password">Confirm Password</label>
                <input type="password" id="passwordConfirm" name="password">
            </div><br>
            <button type="submit" class="primary-button" id="confirmPassword">Confirm</button>
            `);

        $('#password').focus();

        let checks = ['password', 'passwordConfirm']
        checks.forEach(check => {
            $(`#${check}`).on('input', () => {
                if ($(`#${check}`).val() != '') {
                    $(`#${check}Row`).addClass('form-row-active')
                } else {
                    $(`#${check}Row`).removeClass('form-row-active')
                }
            });
        });
        $(`.modal-close`).click(() => {
            this.exitingModal(`.modal-background`);
        });
        $(`#confirmPassword`).click(() => {
            let data = {
                password: $('#password').val(),
                passwordConfirm: $('#passwordConfirm').val()
            };

            this.exitingModal(`.modal-background`);

            setTimeout(() => {
                callback(data, section);
            }, tools.timeTransition+50);
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
            window.location.href = `/search?source=all&target=${this.searchInput.val()}`;
        } else {
            modals.alertMsg('Oops', 'Looks like you forgot to type something.');
        }
    }
}

class MangaViewer {
    constructor() {
        this.url_args = tools.urlArgs();
        
        if (document.location.href.indexOf('manga_viewer') > -1) {
            this.initialBehavior();
            this.searching();
            this.ratingBehavior();
            this.favoriteBehavior();
            this.continueReadingBehavior();
        }
    }

    initialBehavior() {
        if (!this.url_args.hasOwnProperty('id') ||  this.url_args.id == '') {
            modals.errorMsg('No ID inserted.');
        } else if (!this.url_args.hasOwnProperty('source') || this.url_args.source == '') {
            modals.errorMsg('No source inserted.');
        }
    }

    async searching () {
        modals.loadingMsg();
        let manga = await tools.asyncFetch('GET',`/api/manga/view/${this.url_args.source}/${this.url_args.id}`);
        modals.exitingModal(`.modal-background`);

        tools.checkResponse(manga, this.renderManga);
    }

    renderManga (manga) {
        $('#mangaSource').text(tools.capitalize(manga.source));
        $('#mangaImage').attr('src', manga.image);
        $('#mangaTitle').text(manga.title);

        $('#mangaAuthors').text(manga.author.join(', '));
        $('#mangaStatus').text(manga.status);
        $('#mangaGenres').text(manga.genres.join(', '));
        $('#mangaUpdated').text(manga.updated);
        $('#mangaViews').text(manga.views);

        $('#mangaDescription').text(manga.description);

        $('.chapter-no').remove();

        manga.chapters.forEach(ch => {
            let chapter = $(
            `<li class="chapter-no">
                <a href="${ch.chapter_link}" class="">${ch.title}.</a>
                <div class="last-updated">${ch.updated}.</div>
            </li>`
            )
            if (ch.read) {
                chapter.addClass('chapter-read');
            }
            chapter.appendTo('.chapter-list');
        });
        mangaViewer.endingLoading();
    }

    async ratingBehavior() {
        for (let i = 1; i <= 5; i++) {
            $(`#starClassif${i}`).click(() => {
                this.doingAction('rating', i, this.refreshingRating.bind(this));
            });
            $(`#starClassif${i}`).mouseenter(() => {
                for (let j = 0; j <= i; j++) {
                    $(`#starClassif${j}`).addClass('icon-star-selected');
                }
            });
            $(`#starClassif${i}`).mouseleave(() => {
                for (let j = 0; j <= i; j++) {
                    $(`#starClassif${j}`).removeClass('icon-star-selected');
                }
            });
        }
    }

    async refreshingRating() {
        let rating = await tools.asyncFetch('GET',`/api/users/session/rating/${this.url_args.id}`);
        if (rating.data) {
            $('.icon-star').removeClass('icon-star-rated');
            $(`#starClassif${rating.data}`).addClass('icon-star-rated');
        }
    }
    
    async favoriteBehavior() {
        $('#favoriteButton').click(() => {
            this.doingAction('favorite', 0, this.refreshingFavorite.bind(this));
        });
    }

    async refreshingFavorite() {
        let checkingFavorite = await tools.asyncFetch('GET',`/api/users/session/favorite/${this.url_args.id}`);
        if (checkingFavorite.data.status == 'true') {
            $('#favoriteButton').text('Already favorited');
            $('#bookmark').css('display', 'block');
        } else {
            $('#favoriteButton').text('Favorite It!');
            $('#bookmark').css('display', 'none');
        }
    }

    async continueReadingBehavior() {
        let checkingContinue = await tools.asyncFetch('GET',`/api/users/session/history/latest/${this.url_args.id}`);
        
        if (checkingContinue.status == 200) {
            $('#continueReading').attr('href', checkingContinue.data.chapter_link);
        } else {
            $('.continue-reading').css('display', 'none');
            $('#contReadRelational').css('margin-bottom', '0');
        }
    }

    async doingAction (operation, data = 0, callback = () => {}) {
        let url, string_p;
        if (operation == 'favorite') {
            url = `/api/users/session/favorite/${this.url_args.id}`;
            string_p = 'favorite';
        } else if (operation == 'rating') {
            url = `/api/users/session/rating/${this.url_args.id}/${data}`;
            string_p = 'rate';
        }

        let checkingLogin = await tools.asyncFetch('GET','/api/users/session/is_alive');
        if (checkingLogin.status == 200) {
            await tools.asyncFetch('POST', url);
            callback();
        } else {
            modals.alertMsg('Oops', `You need to be logged in to ${string_p}.`);
        }
    }

    async endingLoading () {
        $('.while-loading').toggleClass('while-loading');

        let rating = await tools.asyncFetch('GET',`/api/users/session/rating/${this.url_args.id}`);
        // make a range from 1 to rating.data
        if (rating.data) {
            for (let i = 1; i <= rating.data; i++) {
                $(`#starClassif${i}`).addClass('icon-star-selected');
                $(`#starClassif${rating.data}`).addClass('icon-star-rated');
            }
        }

        let checkingLogin = await tools.asyncFetch('GET','/api/users/session/is_alive');
        if (checkingLogin.status == 200) {
            let checkingFavorite = await tools.asyncFetch('GET',`/api/users/session/favorite/${this.url_args.id}`);
            if (checkingFavorite.data.status == 'true') {
                $('#favoriteButton').text('Already favorited');
                $('#bookmark').css('display', 'block');
            }
        } else {
            $('#favoriteButton').text('Login to favorite');
        }
    }
}

class ChapterViewer {
    constructor () {
        this.url_args = tools.urlArgs();
        this.cardChapter = $('#chapterTarget').clone();

        if (document.location.href.indexOf('chapter_viewer') > -1) {
            this.initialBehavior()
        }
    }

    async initialBehavior() {
        $('footer').hide();

        if (!this.url_args.hasOwnProperty('id') ||  this.url_args.id == '') {
            modals.errorMsg('No ID inserted.');
        } else if (!this.url_args.hasOwnProperty('source') || this.url_args.source == '') {
            modals.errorMsg('No source inserted.');
        }

        modals.loadingMsg();
        this.navbarCreator();
        let chapters = await tools.asyncFetch('GET',`/api/manga/chapter/${this.url_args.source}/${this.url_args.id}`);
        modals.exitingModal(`.modal-background`);

        tools.checkResponse(chapters, this.renderChapter.bind(this));
    }

    renderChapter(chapter) {
        $('#mangaTitle').text(chapter.title);
        if (chapter.manga_title != '' || !chapter.manga_title) {
            $('#mangaPage').text(chapter.manga_title);
            $('#mangaPage').attr('href', chapter.manga_page);
        } else {
            $('#mangaPage').remove();
        }

        // count the number of chapters
        $('.number-pages').text(chapter.chapters.length);
        $('#navPreviousPage').attr('href', chapter.prev_chapter);
        $('#navNextPage').attr('href', chapter.next_chapter);

        if (chapter.prev_chapter == '#') {
            $('.icon-previous').addClass('icon-disabled');
            $('#navPreviousPage').addClass('button-disabled');
            $('#navPreviousPage').attr('href', '#');
            $('#navPreviousPage').click(() => {
                modals.alertMsg('Oops', "There's no chapter behind this one.")
            })
        } else if (chapter.next_chapter == '#') {
            $('.icon-next').addClass('icon-disabled');
            $('#navNextPage').addClass('button-disabled');
            $('#navNextPage').attr('href', '#');
            $('#navNextPage').click(() => {
                modals.alertMsg('Oh no. T-T', "You've reached the last chapter.")
            })
        }

        this.populateLikeManga(chapter.chapters);
    }

    populateLikeManga(pages) {
        $('.chapter-container').empty();

        pages.forEach(pg => {
            let card = this.cardChapter.clone();
            card.addClass('card-target-active');
            card.empty();
            $(`<img src="${pg}" class="chapter-image">`).appendTo(card);
            card.appendTo('.chapter-container');
        });

        $('.while-loading').toggleClass('while-loading');
    }

    populateLikeWebtoon (pages) {
        $('.chapter-container').empty();

        let card = this.cardChapter.clone();
        let img = card.find('.chapter-link').clone();
        pages.forEach(pg => {
            img.attr('src', pg);
            img.appendTo(card);
        });
        card.appendTo('.chapter-container');
    }

    navbarCreator() {
        $(`<div class="navbar-mobile">
            <div class="menu-navbar">
                <ul class="menu-itself">
                    <a class="icon icon-previous menu-item-adj" id="navPreviousPage" href=""></a>
                    <li class="icon icon-scroll-up menu-item-adj" id="navScrollUp"></li>
                    <li class="icon icon-colapse menu-item" id="navColapseMenu"></li>
                    <li class="icon icon-scroll-down menu-item-adj" id="navScrollDown"></li>
                    <a class="icon icon-next menu-item-adj" id="navNextPage" href=""></a>
                </ul>
            </div>
        </div>`).appendTo('body');
        this.navbarBehavior();
    }

    navbarBehavior() {
        $('#navScrollUp').click(() => {
            $('html, body').animate({
                scrollTop: $('html, body').scrollTop() - 400 
            }, 10);
        });

        $('#navScrollDown').click(() => {
            $('html, body').animate({
                scrollTop: $('html, body').scrollTop() + 400 
            }, 10);
        });

        $('#navColapseMenu').click(() => {
            $('.menu-itself').toggleClass('disabled');
            if ($('.menu-itself').hasClass('disabled')) {
                $('.menu-item-adj').css('opacity', 0);
                setTimeout(() => {
                    $('.menu-item-adj').css({'width': 0, 'padding': '1em 0'});
                    $('.menu-itself').css('gap', '0');
                }, 500);
            } else {
                $('.menu-item-adj').css({
                    width: '1em',
                    padding: '1em'
                });
                $('.menu-itself').css('gap', '1em');
                setTimeout(() => {
                    $('.menu-item-adj').css('opacity', '1');
                }, 500);
            }
        });
    }
}

class SearchSource {
    constructor () {
        this.sources = ['manganato','mangavibe', 'mangalife','mangahere']

        if (document.location.href.indexOf('search') > -1) {
            this.initialization()
        }
    }

    async initialization () {
        // commented by now cuz it must exhibit in the order that
        // the sources was sended by the server.
        this.sources = await tools.asyncFetch('GET', '/api/manga/avaliable_sources');

        if (this.sources.status == 200) {
            this.sources = Object.keys(this.sources.data)
        } else {
            modals.errorMsg(this.sources.message)
        }

        let url_args = tools.urlArgs()

        if (!url_args.hasOwnProperty('source') || url_args.source == '') {
            modals.errorMsg('No source inserted.');
        } else if (url_args.source != 'all' && !this.sources.includes(url_args.source)) {
            modals.errorMsg('Invalid source.');
        } else if (!url_args.hasOwnProperty('target') || url_args.target == '') {
            modals.errorMsg('No target inserted.');
        }

        $('#searchNameTarget').text(url_args.target.replace(/_/g, ' ').replace(/%20/g, ' '));

        if (url_args.source == 'all') {
            this.sources.forEach(async source => {
                await this.sourceSearch(source, url_args.target);
            });
        } else {
            await this.sourceSearch(url_args.source, url_args.target);
        }
    }

    creatingSearchContainer(source) {
        $('<div>').attr('id', `${source}`).addClass('source-container').appendTo('.search')
        $('<div>').attr('id', `${source}-header`).addClass('source-header').addClass('searching').appendTo(`#${source}`)
        $('<h2>').text(`${source}`).appendTo(`#${source}-header`)
        $('<div>').addClass('source-content').appendTo(`#${source}`)
    }

    async sourceSearch (source, target) {
        this.creatingSearchContainer(source);

        // locating elements
        let source_header = $(`#${source}-header`)
        let container = $(`#${source}`).find('.source-content')

        let results = await tools.asyncFetch('GET', `/api/manga/search/${source}/${target}`)
        
        if (results.status == 500 || results.status == 400 || results.status == 404) {
            source_header.toggleClass('searching')
            source_header.toggleClass('error')
        } else {
            let keys = Object.keys(results.data)
            source_header.toggleClass('searching')

            container.toggleClass('active')

            let index = 0
            keys.forEach(key => {
                let card = this.renderCard(
                    `${key}`,
                    results.data[`${key}`].author,
                    results.data[`${key}`].chapter,
                    results.data[`${key}`].image,
                    results.data[`${key}`].link,
                    results.data[`${key}`].chapter_link,
                    results.data[`${key}`].updated,
                )
                
                container.append(card)
                $(`#card${index}`).css({opacity: 0})
                setTimeout(() => {
                    $(`#card${index}`).animate({
                        opacity: 1
                    }, tools.timeTransition, () => {$(`#card${index}`).css({opacity: 1})})
                }, 2000);
                index ++
            })
        }
    }

    renderCard (title, author, chapter, image_url, manga_link, chapter_link, updated) {
        return $(`
        <div id="${title}" class="card-result">
            <div class="card-result-image">
                <img class="card-image" src="${image_url}" alt="${title} cover">
            </div>
            <div class="card-result-info">
                <h2>
                    <a href="${manga_link}">
                        <span class="card-title">
                            ${title}
                        </span>
                    </a>
                </h2>
                <p>
                    <span class="card-link-text">
                        ${author}
                    </span>
                </p>
                <p>
                    <a class="card-link" href="${chapter_link}">
                        <span class="card-link-text">
                            ${chapter} <br> ${updated}
                        </span>
                    </a>
                </p>
            </div>
        </div>
        `)
    }
}

class Login {
    constructor () {
        if (document.location.href.indexOf('login') > -1) {
            this.initialization('login')
        } else if (document.location.href.indexOf('register') > -1) {
            this.initialization('register')
        }
    }

    initialization (section) {
        ['.seach-menu','#headOptionHome','#headOptionManga'].forEach((item) => {
            $(item).hide();
        })

        $('#email').focus();

        let checks = ['email','password', 'passwordConfirm']
        checks.forEach(check => {
            $(`#${check}`).on('input', () => {
                if ($(`#${check}`).val() != '') {
                    $(`#${check}Row`).addClass('form-row-active')
                } else {
                    $(`#${check}Row`).removeClass('form-row-active')
                }
            });
        });

        $('#primaryButton').click((e) => {
            e.preventDefault();
            this.validate(section)
        });
        $('#secondaryButton').click((e) => {
            e.preventDefault();
            if (section == 'login') {
                document.location.href = '/register'
            } else {
                document.location.href = '/login'
            }
        });
    }

    validate(section) {
        this.email = $('#email').val();
        this.password = $('#password').val();
        this.passwordConfirm = $('#passwordConfirm').val();

        if (this.email == '') {
            modals.alertMsg('Oops', 'No username inserted.');
        } else if (this.password == '') {
            modals.alertMsg('Oops', 'No password inserted.');
        } else if (this.passwordConfirm && this.passwordConfirm != this.password) {
            modals.alertMsg('Oops', 'Passwords do not match.');
        } else {
            if (section == 'login') {
                this.login()
            } else if (section == 'register') {
                if (tools.validatePasswordSecurity(this.password) == false) {
                    modals.alertMsg('Oops', 'Password must be at least 8 characters and contain at least one number, one uppercase and one lowercase letter.');
                } else {
                    this.register()
                }
            }
        }
    }
    
    async login () {
        let resp = await tools.asyncFetch('GET',`/api/users/login?email=${this.email}&password=${this.password}`);

        if (resp.status == 200) {
            window.location.href = '/';
        } else {
            modals.alertMsg('Oops', resp.message);
        }
    }

    async register () {
        let resp = await tools.asyncFetch(
            'POST',
            '/api/users/login',
            {email: this.email, password: this.password}
        );

        if (resp.status == 200) {
            modals.alertMsg('OK!', resp.message);
            $('.modal-close').remove()
            setTimeout(() => {
                window.location.href = '/profile';
            }, tools.timeError);
        } else {
            modals.alertMsg('Oops', resp.message);
        }
    }
}

class Profile {
    constructor () {
        if (document.location.href.includes('profile')) {
            this.initialization()
        }
    }

    initialization () {
        this.getProfile();
        
        this.profileBehavior();
        
        if (document.location.href.includes('profile/history')) {
            this.historyBehavior()
        }
    }

    profileBehavior () {
        $('#mainPageUpdate').click((e) => {
            this.updateInfo({
                password:1,
                passwordConfirm:1,
            }, 'main_section')
        });

        $('#usernameUpdate').click(() => {
            if ($('#usrnm').val().length > 6) {
                modals.confirmPasswordMsg(this.updateInfo.bind(this), 'username')
            } else {
                modals.alertMsg('Oops', 'Username must be at least 6 characters.')
            }
        });

        $('#passwordUpdate').click(() => {
            if ($('#pwUpdt').val() == $('#pwUpdtCnfm').val()) {
                if (tools.validatePasswordSecurity($('#pwUpdt').val())) {
                    modals.confirmPasswordMsg(this.updateInfo.bind(this), 'password')
                } else {
                    modals.alertMsg('Oops', 'Password must be at least 8 characters and contain at least one number, one uppercase and one lowercase letter.')
                }
            } else {
                modals.alertMsg('Oops', 'Passwords do not match.')
            }
        });

        $('#imageProfile').click(() => {
            modals.alertMsg('Oops', 'This feature is not available yet.')
        });

        $('#logout').click(() => {
            this.logout()
        });
    }
            
    async getProfile () {
        let profile = await tools.asyncFetch('GET', '/api/users/session/get_profile');
        if (profile.status == 200) {
            $('#mainSection').val(profile.data.user_main_page);
            $('#usernameName').text(profile.data.user_username);
            $('#usrnm').val(profile.data.user_username);
        }
    }

    async updateInfo (data, section) {
        let target = '';

        if (section == 'username') {
            target = $('#usrnm').val();
        } else if (section == 'password') {
            target = $('#pwUpdt').val();
        } else if (section == 'main_section') {
            target = $('#mainSection').val();
        }


        if (data.password != data.passwordConfirm) {
            modals.alertMsg('Oops', "Password doen't match.");
        } else {
            let resp = await tools.asyncFetch(
                'POST',
                `/api/users/session/update/${section}`,
                {password: data.password, target: target}
            );

            if (resp.status == 200) {
                modals.alertMsg('OK!', resp.message);
                $('.modal-close').remove()
                setTimeout(() => {
                    window.location.href = '/profile';
                }, tools.timeError);
            } else {
                modals.alertMsg('Oops', resp.message);
            }
        }
    }

    historyBehavior () {
        $('#resetHistory').click(async () => {
            let resp = await tools.asyncFetch(
                'POST',
                '/api/users/session/history/reset'
            );
            
            if (resp.status == 200) {
                modals.alertMsg('OK!', resp.message);
                $('.modal-close').remove()
                setTimeout(() => {
                    window.location.href = '/profile/history';
                }, tools.timeError);
            }
        });

        this.historyShow()
    }

    async historyShow () {
        let resp = await tools.asyncFetch('GET','/api/users/session/history');
        let cardHistory = $('.li-target').clone();
        $('.li-target').remove();
        resp.data.forEach(item => {
            let card = cardHistory.clone();
            card.find('img').attr('src', item.manga_image);
            card.find('.card-manga-page').text(item.manga_title);
            card.find('.card-manga-page').attr('href', `/manga_viewer?source=${item.manga_source}&id=${item.manga_slug}`);
            if (item.chapter_title != null) {
                card.find('.card-chapter-page').text(item.chapter_title);
                card.find('.card-chapter-page').attr('href', `/chapter_viewer?source=${item.manga_source}&id=${item.chapter_slug}`);
            } else {
                card.find('.card-chapter-page').text('None');
                card.find('.card-chapter-page').attr('href', '');
            }
            $('#historyContainer').append(card);
        });

        if (resp.data.length == 0) {
            $('#historyContainer').append(`
                <div class="card" style="width: 100%;">
                    <div class="card-body" style="width: 100%; text-align: center;">
                        <h1 class="card-title">No history found</h1>
                        <p class="card-text">You have not readed any manga yet.</p>
                    </div>
                </div>
            `);
        }
    }

    logout () {
        tools.asyncFetch('GET', '/api/users/logout')
        .then(resp => {
            if (resp.status == 200) {
                window.location.href = '/';
            } else {
                modals.alertMsg('Oops', resp.message);
            }
        });
    }
}

class Favorites {
    constructor () {
        if (document.location.href.includes('favorite')) {
            this.card = $('.card-result').clone();
            $('.card-result').remove();
            this.initialization()
        }
    }

    initialization () {
        this.getFavorites();
        
        $('#filterSelect').change(() => {
            this.getFavorites($('#filterSelect').val());
        });
    }

    async getFavorites (filter = 'manga_title') {
        let resp = await tools.asyncFetch('GET', `/api/users/session/favorite/filter/${filter}`);
        console.log(resp);
        if (resp.status == 200) {
            $('#containerTarget').empty();
            resp.data.forEach(item => {
                let cardClone = this.card.clone();
                cardClone.find('#cardImage').attr('src', item.manga_image);
                cardClone.find('#cardTitle').text(item.manga_title);
                cardClone.find('#cardLink').attr('href', `/manga_viewer?source=${item.manga_source}&id=${item.manga_slug}`);
                // cardClone.find('#cardChapter').text(item.chapter_new ? '' : "There's unread chapters");
                $('#containerTarget').append(cardClone);
                $('.card-result').fadeIn(500);
            });
        } 

        if (resp.data.length == 0) {
            $('#containerTarget').append(`
                <div class="card" style="width: 100%;">
                    <div class="card-body" style="width: 100%; text-align: center;">
                        <h1 class="card-title">No Favorites found</h1>
                        <p class="card-text">You have't favorited any manga yet.</p>
                    </div>
                </div>
            `);
        }
    }
}

class Tools {
    constructor () {
        this.timeTransition = 250;
        this.timeError = 2500;
    }

    capitalize(word) {
        return word[0].toUpperCase() + word.slice(1).toLowerCase();
    }

    async asyncFetch (method, url, body = {}) {
        let response = ''

        if (method == 'GET') {
            response  = await fetch(url)
        } else if (method == 'POST') {
            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            })
        }
        
        let result = await response.json()
        return result
    }

    urlArgs () {
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        var args = {};
        for (var i = 0; i < vars.length; i++) {
            var pair = vars[i].split("=");
            args[pair[0]] = pair[1];
        }
        return args;
    }

    checkResponse (response, success_func) {
        let deniedResponses = [400, 401, 403, 404, 500]
        
        if (deniedResponses.indexOf(response.status) > -1) {
            if (this.urlArgs().hasOwnProperty('error') && this.urlArgs().error == 'true') {
                modals.errorMsg(response.message);
            } else {
                modals.alertMsg(
                    'Oops', 
                    `Oh no, I encountered a error.<br>I'll refresh the page to verify if it happens again.<br><br>
                    ${response.message}`
                );
                setTimeout(() => {
                    let current_url = window.location.href;
                    window.location.href = `${current_url}&error=true`;
                }, this.timeError);
            }
        } else {
            success_func(response.data);
        }
    }

    validatePasswordSecurity (password) {
        let password_strength = 0;
        if (password.length > 6) {
            password_strength++;
        }
        if (password.match(/[a-z]/)) {
            password_strength++;
        }
        if (password.match(/[A-Z]/)) {
            password_strength++;
        }
        if (password.match(/[0-9]/)) {
            password_strength++;
        }
        if (password.match(/[^a-zA-Z0-9]/)) {
            password_strength++;
        }

        if (password_strength < 3) {
            return false;
        } else {
            return true;
        }
    }
}

let tools = new Tools();
let header = new Header();
let modals = new Modals();
let searchBar = new SearchBar();
let mangaViewer = new MangaViewer();
let chapterViewer = new ChapterViewer();
let searchSource = new SearchSource();
let login = new Login();
let profile = new Profile();
let favorites = new Favorites();