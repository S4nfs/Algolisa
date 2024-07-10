function climbingLeaderboard(ranked, player) {
  let sortRanked = ranked.sort((a, b) => a - b) // [60,75,80,90,90,100]
  let rank = ranked.length + 1
  for (let i = 0; i < player.length; i++) {
    let position
    for (let j = 0; j < sortRanked.length; j++) {
      if ((player[i] < sortRanked[j] && j == 0) || (player[i] >= sortRanked[j] && player[i] < sortRanked[j + 1]) || player[i] > sortRanked[sortRanked.length - 1]) {
        rank--
        position = rank
      }
    }
    console.log(rank)
  }
}

console.log(climbingLeaderboard([100, 90, 90, 80, 75, 60], [50, 65, 77, 90, 102]))

console.log(10.1000000000000002 === 10.1)
