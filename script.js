// script.js
document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const productLinkInput = document.getElementById('productLink');
    const resultsContainer = document.getElementById('resultsContainer');
    const loader = document.getElementById('loader');

    // Adres naszego serwera w Pythonie
    const API_URL = 'https://qc-finder.onrender.com/find_qc'; // <<< TWOJA NOWA LINIA

    const performSearch = async () => {
        const productUrl = productLinkInput.value.trim();
        if (!productUrl) {
            alert('Proszę wkleić link!');
            return;
        }

        // Czyścimy poprzednie wyniki i pokazujemy kółko ładowania
        resultsContainer.innerHTML = '';
        loader.style.display = 'block';

        try {
            // Wysyłamy link do naszego backendu
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_url: productUrl }),
            });

            if (!response.ok) {
                throw new Error('Błąd serwera. Sprawdź konsolę backendu.');
            }

            const data = await response.json();

            // Ukrywamy kółko ładowania
            loader.style.display = 'none';

            if (data.images && data.images.length > 0) {
                // Jeśli znaleziono zdjęcia, tworzymy elementy <img> i dodajemy je do strony
                data.images.forEach(imageUrl => {
                    const img = document.createElement('img');
                    img.src = imageUrl;
                    img.alt = 'Zdjęcie QC';
                    resultsContainer.appendChild(img);
                });
            } else {
                // Jeśli nie ma zdjęć, pokazujemy komunikat
                resultsContainer.innerHTML = '<p>Nie znaleziono zdjęć QC dla tego produktu. Spróbuj z innym linkiem.</p>';
            }
        } catch (error) {
            loader.style.display = 'none';
            resultsContainer.innerHTML = `<p>Wystąpił błąd: ${error.message}</p>`;
            console.error('Błąd:', error);
        }
    };

    searchButton.addEventListener('click', performSearch);
    
    // Umożliwia wyszukiwanie po wciśnięciu Enter w polu tekstowym
    productLinkInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            performSearch();
        }
    });
});