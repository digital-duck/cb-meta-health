const translations = {
  en: {
    'app.title': '元健康 Meta-Health',
    'app.tagline': 'Movement, Eating, and Mind as One Practice',
    'nav.about': 'About',
    'nav.settings': 'Settings',
    'home.subtitle': 'Choose a domain to explore',
    'home.filter.all': 'All',
    'home.filter.level': 'Level',
    'card.nodes': 'nodes',
    'card.edges': 'edges',
    'card.explore': 'Explore Concept-Graph',
    'card.read': 'Read book',
    'domain.back': '← Back',
    'domain.openFullscreen': 'Open fullscreen',
    'about.title': 'About concept-book',
    'loading': 'Loading…',
  },
  zh: {
    'app.title': '元健康',
    'app.tagline': '运动、饮食与心神的一体修炼',
  },
}

let _locale = localStorage.getItem('cb-lang') || 'en'

export function t(key) {
  // Per-key fallback to English, so a locale only needs to override the keys it translates.
  return translations[_locale]?.[key] ?? translations.en[key] ?? key
}

export function setLocale(lang) {
  _locale = lang
  localStorage.setItem('cb-lang', lang)
}

export function getLocale() {
  return _locale
}
