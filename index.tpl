<!DOCTYPE html>
<html>
<head>
<style>
h2, h3 {
  font-family: Helvetica, sans-serif;
}
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>
</head>
<body>

<h2>DevOps School APP</h2>

<form action="formdata" method="post" id="data"></form>
<p><select name="list1" form="data">
 <option>Выберите из списка</option>
 <option>Option</option>
 <option>Textarea</option>
 <option>Label</option>
 <option>Fieldset</option>
 <option>Legend</option>
</select></p>
<p><input type="submit" value="Отправить" form="data"></p>

<h3>Games in previous month</h3>
<table>
  <tr>
    <th>Date</th>
    <th>Away Team</th>
    <th>Home Team</th>
    <th>Scores</th>
  </tr>
  {% for line in games %}
  <tr>
    <td>{{ line[0] }}</td>
    <td>{{ line[1] }}</td>
    <td>{{ line[2] }}</td>
    <td>{{ line[3] }}</td>
  </tr>
 {% endfor %}
</table>

<h3>Top TimeOnIce players </h3>
<table>
    <tr>
      <th>Date</th>
      <th>Name</th>
      <th>TimeOnIce</th>
    </tr>
    {% for line in players %}
    <tr>
      <td>{{ line[0] }}</td>
      <td>{{ line[1] }}</td>
      <td>{{ line[2] }}</td>
    </tr>
   {% endfor %}
  </table>

</body>
</html>
