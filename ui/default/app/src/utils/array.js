Array.prototype.groupBy = function (field) {
  let groupedArr = [];
  this.forEach(function (e) {
    //look for an existent group
    let group = groupedArr.find(g => g[ 'field' ] === e[ field ]);
    if (group == undefined) {
      //add new group if it doesn't exist
      group = { field: e[ field ], groupList: [] };
      groupedArr.push(group);
    }

    //add the element to the group
    group.groupList.push(e);
  });

  return groupedArr;
}