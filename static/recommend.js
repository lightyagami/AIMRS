$(function() {
  // Load History and Watchlist on Startup
  displayRecentlyViewed();
  displayWatchlist();

  // Button will be disabled until we type anything inside the input field
  const source = document.getElementById('autoComplete');
  const inputHandler = function(e) {
    if(e.target.value==""){
      $('.movie-button').attr('disabled', true);
    }
    else{
      $('.movie-button').attr('disabled', false);
    }
  }
  source.addEventListener('input', inputHandler);

  $('.movie-button').on('click',function(){
    var my_api_key = '71bdf22d8b06fde7b7b67d170d00b0c8';
    var title = $('.movie').val();
    if (title=="") {
      $('.results').css('display','none');
      $('.fail').css('display','block');
    }
    else{
      load_details(my_api_key,title);
    }
  });
});

// will be invoked when clicking on the recommended movies
async function recommendcard(e){
  var my_api_key = '71bdf22d8b06fde7b7b67d170d00b0c8';
  var title_with_score = e.getAttribute('title');
  var title = title_with_score.split(' (')[0]; // Strip the score for API search
  
  $("#loader").fadeIn();
  try {
    const movie = await $.ajax({
      type: 'GET',
      url:'https://api.themoviedb.org/3/search/movie?api_key='+my_api_key+'&query='+title+'&language=en-US',
    });

    if(movie.results.length<1){
      $('.fail').css('display','block');
      $('.results').css('display','none');
      $("#loader").fadeOut();
    }
    else{
      $('.trending-section').hide();
      $('.fail').css('display','none');
      $('.results').css('display','block');
      var movie_id = movie.results[0].id;
      movie_recs(title, movie_id, my_api_key);
    }
  } catch (error) {
    alert('Invalid Request');
    $("#loader").fadeOut();
  }
}

// get the basic details of the movie from the API (based on the name of the movie)
async function load_details(my_api_key,title){
  $("#loader").fadeIn();
  try {
    const movie = await $.ajax({
      type: 'GET',
      url:'https://api.themoviedb.org/3/search/movie?api_key='+my_api_key+'&query='+title+'&language=en-US',
    });

    if(movie.results.length<1){
      $('.fail').css('display','block');
      $('.results').css('display','none');
      $("#loader").fadeOut();
    }
    else{
      $('.trending-section').hide();
      $('.fail').css('display','none');
      $('.results').css('display','block');
      var movie_id = movie.results[0].id;
      var movie_title = movie.results[0].title;
      movie_recs(movie_title,movie_id,my_api_key);
    }
  } catch (error) {
    alert('Invalid Request');
    $("#loader").fadeOut();
  }
}

// passing the movie name to get the similar movies from python's flask
async function movie_recs(movie_title,movie_id,my_api_key){
  try {
    const recs = await $.ajax({
      type:'POST',
      url:"/similarity",
      data:{'name':movie_title},
    });

    if(recs=="Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies"){
      $('.fail').css('display','block');
      $('.results').css('display','none');
      $("#loader").fadeOut();
    }
    else {
      $('.fail').css('display','none');
      $('.results').css('display','block');
      var movie_arr = recs.split('---');
      var arr = [];
      for(var i=0; i < movie_arr.length; i++){
        arr.push(movie_arr[i]);
      }
      get_movie_details(movie_id,my_api_key,arr,movie_title);
    }
  } catch (error) {
    alert("error recs");
    $("#loader").fadeOut();
  }
}

// get all the details of the movie using the movie id.
async function get_movie_details(movie_id,my_api_key,arr,movie_title) {
  try {
    const movie_details = await $.ajax({
      type:'GET',
      url:'https://api.themoviedb.org/3/movie/'+movie_id+'?api_key='+my_api_key,
    });
    show_details(movie_details,arr,movie_title,my_api_key,movie_id);
  } catch (error) {
    alert("API Error!");
    $("#loader").fadeOut();
  }
}

// get the reviews of the movie
async function get_reviews(movie_id, my_api_key) {
  try {
    const res = await $.ajax({
      type: 'GET',
      url: 'https://api.themoviedb.org/3/movie/' + movie_id + '/reviews?api_key=' + my_api_key + '&language=en-US',
    });
    let reviews = [];
    for (var i in res.results) {
      reviews.push(res.results[i].content);
    }
    return reviews;
  } catch (error) {
    return [];
  }
}

// passing all the details to python's flask for displaying and scraping the movie reviews using imdb id
async function show_details(movie_details,arr,movie_title,my_api_key,movie_id){
  var imdb_id = movie_details.imdb_id;
  var poster = movie_details.poster_path ? 'https://image.tmdb.org/t/p/original'+movie_details.poster_path : '../static/image.jpg';
  var overview = movie_details.overview;
  var genres = movie_details.genres;
  var rating = movie_details.vote_average;
  var vote_count = movie_details.vote_count;
  var release_date = new Date(movie_details.release_date);
  var runtime = parseInt(movie_details.runtime);
  var status = movie_details.status;
  var genre_list = []
  for (var genre in genres){
    genre_list.push(genres[genre].name);
  }
  var my_genre = genre_list.join(", ");
  if(runtime%60==0){
    runtime = Math.floor(runtime/60)+" hour(s)"
  }
  else {
    runtime = Math.floor(runtime/60)+" hour(s) "+(runtime%60)+" min(s)"
  }

  // Fetch everything in parallel
  const [arr_poster, movie_cast, reviews_from_browser] = await Promise.all([
    get_movie_posters_async(arr, my_api_key),
    get_movie_cast_async(movie_id, my_api_key),
    get_reviews(movie_id, my_api_key)
  ]);
  
  const ind_cast = await get_individual_cast_async(movie_cast, my_api_key);
  
  const details = {
    'title':movie_title,
      'cast_ids':JSON.stringify(movie_cast.cast_ids),
      'cast_names':JSON.stringify(movie_cast.cast_names),
      'cast_chars':JSON.stringify(movie_cast.cast_chars),
      'cast_profiles':JSON.stringify(movie_cast.cast_profiles),
      'cast_bdays':JSON.stringify(ind_cast.cast_bdays),
      'cast_bios':JSON.stringify(ind_cast.cast_bios),
      'cast_places':JSON.stringify(ind_cast.cast_places),
      'imdb_id':imdb_id,
      'poster':poster,
      'genres':my_genre,
      'overview':overview,
      'rating':rating,
      'vote_count':vote_count.toLocaleString(),
      'release_date':release_date.toDateString().split(' ').slice(1).join(' '),
      'runtime':runtime,
      'status':status,
      'movie_id':movie_id,
      'rec_movies':JSON.stringify(arr),
      'rec_posters':JSON.stringify(arr_poster),
      'browser_reviews': JSON.stringify(reviews_from_browser)
  }

  $.ajax({
    type:'POST',
    data:details,
    url:"/recommend",
    dataType: 'html',
    complete: function(){
      $("#loader").fadeOut();
    },
    success: function(response) {
      $('.results').html(response);
      $('#autoComplete').val('');
      $(window).scrollTop(0);
      saveToRecent(movie_title, poster);
    }
  });
}

// get the details of individual cast (Asynchronous)
async function get_individual_cast_async(movie_cast, my_api_key) {
    const cast_bdays = [];
    const cast_bios = [];
    const cast_places = [];
    
    const promises = movie_cast.cast_ids.map(id => 
      $.ajax({
        type:'GET',
        url:'https://api.themoviedb.org/3/person/'+id+'?api_key='+my_api_key,
      })
    );

    try {
      const results = await Promise.all(promises);
      results.forEach(cast_details => {
        cast_bdays.push((new Date(cast_details.birthday)).toDateString().split(' ').slice(1).join(' '));
        cast_bios.push(cast_details.biography);
        cast_places.push(cast_details.place_of_birth);
      });
    } catch (e) {
      console.error("Error fetching cast details", e);
    }
    
    return {cast_bdays, cast_bios, cast_places};
}

// getting the details of the cast for the requested movie (Asynchronous)
async function get_movie_cast_async(movie_id, my_api_key){
    const cast_ids= [];
    const cast_names = [];
    const cast_chars = [];
    const cast_profiles = [];

    try {
      const my_movie = await $.ajax({
        type:'GET',
        url:"https://api.themoviedb.org/3/movie/"+movie_id+"/credits?api_key="+my_api_key,
      });

      let top_cast = my_movie.cast.length >= 10 ? my_movie.cast.slice(0, 10) : my_movie.cast.slice(0, 5);
      
      top_cast.forEach(cast => {
        cast_ids.push(cast.id)
        cast_names.push(cast.name);
        cast_chars.push(cast.character);
        cast_profiles.push(cast.profile_path ? "https://image.tmdb.org/t/p/original"+cast.profile_path : "../static/image.jpg");
      });
    } catch (e) {
      console.error("Error fetching cast", e);
    }

    return {cast_ids, cast_names, cast_chars, cast_profiles};
}

// getting posters for all the recommended movies (Asynchronous)
async function get_movie_posters_async(arr, my_api_key){
  const promises = arr.map(item => {
    var title_part = item.split('|||')[0]; 
    var title = title_part.split(' (')[0]; 
    return $.ajax({
      type:'GET',
      url:'https://api.themoviedb.org/3/search/movie?api_key='+my_api_key+'&query='+title,
    });
  });

  try {
    const results = await Promise.all(promises);
    return results.map(m_data => {
      if(m_data.results && m_data.results.length > 0) {
        return 'https://image.tmdb.org/t/p/original'+m_data.results[0].poster_path;
      }
      return '../static/image.jpg';
    });
  } catch (e) {
    return arr.map(() => '../static/image.jpg');
  }
}

function saveToRecent(title, poster) {
    let recent = JSON.parse(localStorage.getItem('recentMovies') || '[]');
    recent = recent.filter(m => m.title !== title);
    recent.unshift({title, poster});
    recent = recent.slice(0, 4);
    localStorage.setItem('recentMovies', JSON.stringify(recent));
    displayRecentlyViewed();
}

function displayRecentlyViewed() {
    let recent = JSON.parse(localStorage.getItem('recentMovies') || '[]');
    if (recent.length > 0) {
        $('#recentSection').fadeIn();
        let html = '';
        recent.forEach(m => {
            html += `
                <div class="col-6 col-md-3 mb-3">
                    <div class="card h-100" style="cursor:pointer; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); border-radius: 16px; transition: 0.3s;" title="${m.title}" onclick="recommendcard(this)">
                        <img src="${m.poster}" class="card-img-top" style="height: 120px; object-fit: cover; border-top-left-radius: 16px; border-top-right-radius: 16px;">
                        <div class="p-2 text-center">
                            <span style="font-size: 0.7rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; color: white;">${m.title}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        $('#recentMovies').html(html);
    } else {
        $('#recentSection').hide();
    }
}

function clearRecent() {
    localStorage.removeItem('recentMovies');
    $('#recentSection').fadeOut(300, function() {
        $('#recentMovies').html('');
    });
}

function openTrailer(movie_title) {
    var my_api_key = '71bdf22d8b06fde7b7b67d170d00b0c8';
    $.ajax({
        type: 'GET',
        url: 'https://api.themoviedb.org/3/search/movie?api_key=' + my_api_key + '&query=' + movie_title,
        success: function(searchRes) {
            if (searchRes.results.length > 0) {
                var movie_id = searchRes.results[0].id;
                $.ajax({
                    type: 'GET',
                    url: 'https://api.themoviedb.org/3/movie/' + movie_id + '/videos?api_key=' + my_api_key,
                    success: function(res) {
                        var trailer = res.results.find(v => v.type === 'Trailer' && v.site === 'YouTube');
                        if (trailer) {
                            $('#trailerFrame').attr('src', 'https://www.youtube.com/embed/' + trailer.key + '?autoplay=1');
                            $('#trailerModal').modal('show');
                        } else {
                            alert('No trailer found for this title.');
                        }
                    }
                });
            } else {
                alert('Movie not found on TMDB.');
            }
        }
    });
}

$('#trailerModal').on('hidden.bs.modal', function () {
    $('#trailerFrame').attr('src', '');
});

function toggleWatchlist(title, poster) {
    let watchlist = JSON.parse(localStorage.getItem('watchlistMovies') || '[]');
    let index = watchlist.findIndex(m => m.title === title);
    
    if (index > -1) {
        watchlist.splice(index, 1);
        $('#watchlistBtn').html('<i class="fa fa-heart mr-2"></i> ADD TO WATCHLIST').removeClass('btn-danger').addClass('btn-outline-light');
    } else {
        watchlist.push({title, poster});
        $('#watchlistBtn').html('<i class="fa fa-check mr-2"></i> IN WATCHLIST').removeClass('btn-outline-light').addClass('btn-danger');
    }
    
    localStorage.setItem('watchlistMovies', JSON.stringify(watchlist));
    displayWatchlist();
}

function displayWatchlist() {
    let watchlist = JSON.parse(localStorage.getItem('watchlistMovies') || '[]');
    if (watchlist.length > 0) {
        $('#watchlistSection').fadeIn();
        let html = '';
        watchlist.forEach(m => {
            html += `
                <div class="col-6 col-md-3 mb-3">
                    <div class="card h-100" style="cursor:pointer; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); border-radius: 16px; transition: 0.3s;" title="${m.title}" onclick="recommendcard(this)">
                        <img src="${m.poster}" class="card-img-top" style="height: 120px; object-fit: cover; border-top-left-radius: 16px; border-top-right-radius: 16px;">
                        <div class="p-2 text-center">
                            <span style="font-size: 0.7rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; color: white;">${m.title}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        $('#watchlistMovies').html(html);
    } else {
        $('#watchlistSection').hide();
    }
}

function clearWatchlist() {
    localStorage.removeItem('watchlistMovies');
    $('#watchlistSection').fadeOut(300, function() {
        $('#watchlistMovies').html('');
    });
}

function tagSearch(tag) {
    load_details('71bdf22d8b06fde7b7b67d170d00b0c8', tag);
}

function submitReview() {
    var review = $('#userReview').val();
    var movie_id = $('#name').attr('data-id') || "{{movie_id}}"; // We'll need to set this in template
    if (review == "") {
        alert("Please enter a review first!");
        return;
    }

    $.ajax({
        type: 'POST',
        url: '/predict_sentiment',
        data: { 
            'review': review,
            'movie_id': movie_id
        },
        success: function(res) {
            if (res.error) {
                alert(res.error);
            } else {
                // Clear input
                $('#userReview').val('');
                
                // Add to table
                var sentimentHtml = res.sentiment === 'Good' ? 
                    '<span class="badge badge-success px-3 py-2">POSITIVE <i class="fa fa-smile-beam ml-1"></i></span>' :
                    '<span class="badge badge-danger px-3 py-2">NEGATIVE <i class="fa fa-frown ml-1"></i></span>';
                
                var newRow = `
                    <tr class="review-row" data-sentiment="${res.sentiment}" style="animation: fadeIn 0.5s ease forwards;">
                        <td style="font-size: 0.95rem; line-height: 1.7; color: #ddd;">"${res.cleaned_review}"</td>
                        <td class="text-center">${sentimentHtml}</td>
                    </tr>
                `;
                
                $('table tbody').prepend(newRow);
                
                // Update Dashboard stats
                updateSentimentStats();
                
                // Scroll to table if not in view
                $('html, body').animate({
                    scrollTop: $("#sentimentSection").offset().top - 100
                }, 500);
            }
        },
        error: function() {
            alert("Analysis failed.");
        }
    });
}

function updateSentimentStats() {
    var pos = $('.review-row[data-sentiment="Good"]').length;
    var neg = $('.review-row[data-sentiment="Bad"]').length;
    
    $('#posCount').text(pos + ' Positive');
    $('#negCount').text(neg + ' Negative');
    
    var summary = "The majority of viewers responded ";
    if(pos > neg) {
        summary += "<span class='text-success font-weight-bold'>positively</span> to this film, highlighting strong narrative execution and cinematic value.";
    } else if (neg > pos) {
        summary += "<span class='text-danger font-weight-bold'>critically</span>, suggesting areas of improvement in pacing or thematic depth.";
    } else {
        summary += "with <span class='text-warning font-weight-bold'>mixed sentiment</span>, indicating a polarizing reception among the audience.";
    }
    $('#sentimentSummary').html(summary);

    var canvas = document.getElementById('sentimentChart');
    if (canvas) {
        // We need to destroy the old chart or update its data
        // For simplicity, we'll use Chart.js 3+ method if available, 
        // but here we just recreate it (Chart.js handles canvas reuse fairly well if we clear it)
        var ctx = canvas.getContext('2d');
        // Find existing chart instance to destroy
        let chartStatus = Chart.getChart("sentimentChart"); 
        if (chartStatus != undefined) {
          chartStatus.destroy();
        }
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative'],
                datasets: [{
                    data: [pos, neg],
                    backgroundColor: ['#34d399', '#f87171'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                cutout: '70%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}
